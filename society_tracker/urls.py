"""
URL configuration for society_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from accounts import views as account_views
from complaints import views as complaint_views
from dashboard import views as dashboard_views
from notices import views as notice_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", account_views.home, name="home"),
    path("login/", account_views.login_view, name="login"),
    path("logout/", account_views.logout_view, name="logout"),
    path("request-account/", account_views.registration_request_view, name="registration_request"),
    path("profile/", account_views.profile_view, name="profile"),
    path("change-password/", account_views.change_password, name="change_password"),
    path("admin-dashboard/", dashboard_views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/residents/", account_views.resident_list, name="resident_list"),
    path("admin-dashboard/residents/create/", account_views.create_resident, name="create_resident"),
    path("admin-dashboard/registration-requests/", account_views.registration_requests, name="registration_requests"),
    path("admin-dashboard/registration-requests/<int:pk>/<str:action>/", account_views.review_registration_request, name="review_registration_request"),
    path("resident/", complaint_views.resident_home, name="resident_home"),
    path("complaints/new/", complaint_views.create_complaint, name="create_complaint"),
    path("complaints/mine/", complaint_views.my_complaints, name="my_complaints"),
    path("complaints/<int:pk>/", complaint_views.complaint_detail, name="complaint_detail"),
    path("complaints/<int:pk>/update/", complaint_views.update_complaint, name="update_complaint"),
    path("admin-dashboard/complaints/", complaint_views.admin_complaints, name="admin_complaints"),
    path("notices/", notice_views.notice_board, name="notice_board"),
    path("notices/new/", notice_views.create_notice, name="create_notice"),
    path("notices/<int:pk>/delete/", notice_views.delete_notice, name="delete_notice"),
    path("notifications/", notice_views.notifications, name="notifications"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
