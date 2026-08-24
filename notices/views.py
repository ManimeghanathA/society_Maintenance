from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import Profile
from complaints.utils import email_user, notify_user
from .forms import NoticeForm
from .models import Notice, Notification


@login_required
def notice_board(request):
    notices = Notice.objects.all()
    return render(request, "notices/board.html", {"notices": notices})


@role_required(Profile.ADMIN)
def create_notice(request):
    form = NoticeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        notice = form.save(commit=False)
        notice.created_by = request.user
        notice.save()
        residents = User.objects.filter(profile__role=Profile.RESIDENT)
        for resident in residents:
            notify_user(resident, f"New notice: {notice.title}", "/notices/")
            if notice.important:
                email_user("Important society notice", f"{notice.title}\n\n{notice.body}", resident.email)
        messages.success(request, "Notice published.")
        return redirect("notice_board")
    return render(request, "notices/create_notice.html", {"form": form})


@role_required(Profile.ADMIN)
def delete_notice(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method != "POST":
        messages.error(request, "Use the delete button to remove a notice.")
        return redirect("notice_board")
    title = notice.title
    notice.delete()
    messages.success(request, f"Notice deleted: {title}")
    return redirect("notice_board")


@login_required
def notifications(request):
    notes_qs = request.user.notifications.all()
    if request.method == "POST":
        notes_qs.update(read=True)
        return redirect("notifications")
    notes = Paginator(notes_qs, 10).get_page(request.GET.get("page"))
    return render(request, "notices/notifications.html", {"notifications": notes})
