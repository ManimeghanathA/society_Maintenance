from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import Profile
from .forms import ComplaintAdminUpdateForm, ComplaintCreateForm
from .models import Complaint, ComplaintHistory
from .utils import notify_complaint_status


@role_required(Profile.RESIDENT)
def resident_home(request):
    from notices.models import Notice

    notices = Notice.objects.all()[:6]
    counts = {
        "open": request.user.complaints.filter(status=Complaint.OPEN).count(),
        "in_progress": request.user.complaints.filter(status=Complaint.IN_PROGRESS).count(),
        "resolved": request.user.complaints.filter(status=Complaint.RESOLVED).count(),
    }
    return render(request, "complaints/resident_home.html", {"notices": notices, "counts": counts})


@role_required(Profile.RESIDENT)
def create_complaint(request):
    form = ComplaintCreateForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        complaint = form.save(commit=False)
        complaint.resident = request.user
        try:
            complaint.save()
        except Exception as exc:
            form.add_error("image", f"Image upload failed: {exc}")
            messages.error(request, "Complaint was not submitted because the image upload failed.")
            return render(request, "complaints/create_complaint.html", {"form": form})
        ComplaintHistory.objects.create(complaint=complaint, actor=request.user, new_status=complaint.status, note="Complaint raised")
        messages.success(request, "Complaint submitted.")
        return redirect("my_complaints")
    return render(request, "complaints/create_complaint.html", {"form": form})


@role_required(Profile.RESIDENT)
def my_complaints(request):
    complaints = request.user.complaints.all()
    return render(request, "complaints/my_complaints.html", {"complaints": complaints})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    role = getattr(request.user.profile, "role", None)
    if role == Profile.RESIDENT and complaint.resident != request.user:
        messages.error(request, "You can view only your own complaints.")
        return redirect("my_complaints")
    form = ComplaintAdminUpdateForm(instance=complaint) if role == Profile.ADMIN else None
    return render(request, "complaints/detail.html", {"complaint": complaint, "form": form})


@role_required(Profile.ADMIN)
def admin_complaints(request):
    complaints = Complaint.objects.select_related("resident").all()
    category = request.GET.get("category")
    status = request.GET.get("status")
    overdue = request.GET.get("overdue")
    week = request.GET.get("week")
    search = request.GET.get("search")
    sort = request.GET.get("sort", "overdue")

    if category:
        complaints = complaints.filter(category=category)
    if status:
        complaints = complaints.filter(status=status)
    if week:
        start = timezone.datetime.fromisocalendar(int(week[:4]), int(week[-2:]), 1).date()
        complaints = complaints.filter(created_at__date__gte=start, created_at__date__lte=start + timezone.timedelta(days=6))
    if search:
        complaints = complaints.filter(
            Q(category__icontains=search)
            | Q(resident__first_name__icontains=search)
            | Q(resident__last_name__icontains=search)
            | Q(id=int(search.replace("CMP-", "").replace("cmp-", "")) if search.replace("CMP-", "").replace("cmp-", "").isdigit() else -1)
        )

    complaints = list(complaints)
    if overdue:
        complaints = [item for item in complaints if item.is_overdue]

    priority_order = {"high": 0, "medium": 1, "low": 2}
    if sort == "priority_high":
        complaints.sort(key=lambda item: (priority_order.get(item.priority, 9), -item.created_at.timestamp()))
    elif sort == "priority_medium":
        complaints.sort(key=lambda item: (0 if item.priority == "medium" else 1, -item.created_at.timestamp()))
    elif sort == "priority_low":
        complaints.sort(key=lambda item: (0 if item.priority == "low" else 1, -item.created_at.timestamp()))
    elif sort == "old":
        complaints.sort(key=lambda item: item.created_at)
    elif sort == "new":
        complaints.sort(key=lambda item: item.created_at, reverse=True)
    else:
        complaints.sort(key=lambda item: (not item.is_overdue, item.deadline or timezone.localdate(), -item.created_at.timestamp()))

    return render(request, "complaints/admin_list.html", {"complaints": complaints, "categories": Complaint.CATEGORY_CHOICES, "statuses": Complaint.STATUS_CHOICES})


@role_required(Profile.ADMIN)
def update_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    old_status = complaint.status
    form = ComplaintAdminUpdateForm(request.POST, instance=complaint)
    if form.is_valid():
        updated = form.save(commit=False)
        if updated.status == Complaint.RESOLVED and complaint.resolved_at is None:
            updated.resolved_at = timezone.now()
        updated.save()
        note = form.cleaned_data.get("note", "")
        ComplaintHistory.objects.create(complaint=updated, actor=request.user, old_status=old_status, new_status=updated.status, note=note)
        if old_status != updated.status or note:
            notify_complaint_status(updated)
        messages.success(request, "Complaint updated.")
    else:
        messages.error(request, "Please correct the complaint update form.")
    return redirect("complaint_detail", pk=pk)
