from django.db.models import Count
from django.shortcuts import render

from accounts.decorators import role_required
from accounts.models import Profile, RegistrationRequest
from complaints.models import Complaint


@role_required(Profile.ADMIN)
def admin_dashboard(request):
    complaints = Complaint.objects.all()
    status_counts = complaints.values("status").annotate(total=Count("id"))
    category_counts = complaints.values("category").annotate(total=Count("id"))
    priority_counts = complaints.values("priority").annotate(total=Count("id"))
    overdue_count = sum(1 for complaint in complaints if complaint.is_overdue)
    pending_requests = RegistrationRequest.objects.filter(status=RegistrationRequest.PENDING).count()
    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "total": complaints.count(),
            "status_counts": status_counts,
            "category_counts": category_counts,
            "priority_counts": priority_counts,
            "overdue_count": overdue_count,
            "pending_requests": pending_requests,
        },
    )
