# Society Maintenance Tracker - Main README

```
## Please read setup.md for setting up and hosting the application
```

```
Live working link: https://society-maintenance-htn0.onrender.com/login
username: admin@example.com
password: admin123
```


## 1. Project Overview

Society Maintenance Tracker is a Django web application for apartment or society maintenance management. It gives residents a place to raise complaints with optional images, track complaint status, read admin notices, and receive notifications. It gives admins a dashboard to manage residents, approve account creation requests, publish notices, prioritize complaints, update complaint status, set deadlines, and monitor overdue work.

The app uses role-based access:

- Admin users manage the society workflow.
- Resident users raise and track only their own complaints.

Login uses email ID and password. The login page has separate Admin Login and Resident Login sections, and users must log in through the correct section.

## 2. Full Feature List

- Separate admin and resident login panels.
- Email ID used as the login user ID.
- Role-based access control for admin and resident pages.
- Admin can create users as either admin or resident.
- Resident can request account creation with name and email if their email is not found during login.
- Admin can approve or reject resident create requests.
- Approval creates a resident with no usable password and emails a one-time password setup link.
- Resident can change password from My Profile.
- Admin can change password from Admin menu.
- Admin dashboard with complaint totals and overdue counts.
- Resident home dashboard with personal complaint summary.
- Resident can raise complaints with category, description, and optional image.
- Resident can view complaints inside My Complaints.
- Resident can open a complaint and view its complete status history.
- Admin can view and manage all complaints.
- Admin can search complaints by complaint ID, category, or resident name.
- Admin can filter complaints by category, status, week, and overdue state.
- Admin can sort complaints by overdue, priority, newest, and oldest.
- Admin can set complaint priority: Low, Medium, High.
- Admin can set complaint status: Open, In Progress, Resolved.
- Admin can set or change complaint deadline.
- Admin can add optional notes during status updates.
- Every complaint status update creates a history record.
- Resident receives in-app notification and email hook on complaint status updates.
- Admin can publish and delete public notices.
- Important notices are pinned above regular notices.
- Important notices trigger resident email hooks.
- In-app notification page for users.
- Light mode and dark mode toggle with saved browser preference.
- Responsive Bootstrap-based UI.
- PostgreSQL-ready deployment through `DATABASE_URL`.
- Cloudinary-ready image upload through `CLOUDINARY_URL`.
- Render-ready deployment using `render.yaml`.
- Production security settings for secure cookies, HTTPS redirect, Render proxy headers, trusted origins, and upload validation.
- Pagination, image preview, CSV export, unread notification counter, timeline view, and dashboard charts.
- GitHub Actions CI for checks and tests on pushes and pull requests.

## 3. Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Django 5 |
| Frontend | Django Templates, Bootstrap 5, custom CSS |
| Database | PostgreSQL for deployment |
| Local database | PostgreSQL recommended; SQLite was only used for quick internal testing |
| Authentication | Django built-in auth using `User.username = email` |
| Authorization | `Profile.role` with `admin` and `resident` |
| Image upload | Django `ImageField`, Cloudinary in production |
| Email | Django email backend with SMTP settings |
| Static files | WhiteNoise |
| Deployment | Render web service + Render PostgreSQL |
| Production server | Gunicorn |

## 4. Folder/File Responsibility Table

| Path | Responsibility |
| --- | --- |
| `manage.py` | Django command entrypoint for running server, migrations, tests, and custom commands. |
| `society_tracker/settings.py` | Main project settings: installed apps, database config, static/media config, email config, Cloudinary switch, login URLs. |
| `society_tracker/urls.py` | Central URL routing for login, dashboard, complaints, notices, notifications, admin pages. |
| `society_tracker/wsgi.py` | WSGI entrypoint used by Gunicorn on Render. |
| `accounts/models.py` | `Profile` role model and `RegistrationRequest` model. |
| `accounts/forms.py` | Login form, create request form, create user form, change password form. |
| `accounts/views.py` | Login, logout, profile, change password, create user, resident list, account request approval/rejection. |
| `accounts/decorators.py` | `role_required()` decorator for admin/resident page protection. |
| `accounts/utils.py` | User creation and account-created email helper. |
| `accounts/signals.py` | Ensures staff-created users get admin profiles. |
| `accounts/management/commands/bootstrap_admin.py` | Creates the first admin from command line. |
| `complaints/models.py` | `Complaint` and `ComplaintHistory` models, overdue calculation, complaint code. |
| `complaints/forms.py` | Resident complaint creation form and admin complaint update form. |
| `complaints/views.py` | Resident home, raise complaint, My Complaints, complaint detail, admin complaint list, admin update flow. |
| `complaints/utils.py` | In-app notification and email helper for complaint updates. |
| `dashboard/views.py` | Admin dashboard statistics. |
| `notices/models.py` | `Notice` and `Notification` models. |
| `notices/forms.py` | Notice publishing form. |
| `notices/views.py` | Notice board, publish notice, notification list, mark notifications read. |
| `templates/base.html` | Shared layout, header, role-based navigation, light/dark toggle. |
| `templates/accounts/` | Login, profile, password, residents, registration request pages. |
| `templates/complaints/` | Resident and admin complaint pages. |
| `templates/dashboard/` | Admin dashboard template. |
| `templates/notices/` | Notice board, create notice, notifications templates. |
| `static/css/app.css` | Custom responsive UI styling and light/dark theme variables. |
| `requirements.txt` | Python dependencies for local setup and Render deployment. |
| `.env.example` | Template for environment variables. |
| `render.yaml` | Render Blueprint configuration for web service and PostgreSQL database. |
| `SYSTEM_DESIGN.md` | Short system design write-up for submission. |
| `SETUP.md` | Detailed setup, PostgreSQL, Cloudinary, SMTP, Render deployment, and security notes. |

## 5. Complete User Workflows

### Application Entry

1. User opens `/login/`.
2. User chooses either Admin Login or Resident Login.
3. User enters email ID and password.
4. System checks if the email exists.
5. If email exists, Django authenticates the password.
6. System checks the user role.
7. If the role matches the selected login section, the user enters the app.
8. If the role does not match, login is rejected.

### Admin Entry

1. Admin logs in through Admin Login.
2. Admin is redirected to `/admin-dashboard/`.
3. Header shows Dashboard, Manage Complaints, Residents, Public Notice, Create Requests, Notifications, and Admin menu.

### Resident Entry

1. Resident logs in through Resident Login.
2. Resident is redirected to `/resident/`.
3. Header shows Home, Raise Complaint, My Complaints, My Profile, Notices, and Notifications.

## 6. Admin Workflow

1. Admin logs in with email and password.
2. Admin opens Dashboard to see total complaints, overdue complaints, pending account requests, and counts by status/category/priority.
3. Admin opens Manage Complaints.
4. Admin searches, filters, or sorts complaints.
5. Admin opens a complaint.
6. Admin updates priority, status, deadline, and optional note.
7. System saves the complaint changes.
8. System creates a `ComplaintHistory` row.
9. System creates a resident notification.
10. System attempts to send resident email.
11. Admin can open Residents to see resident accounts and complaint counts.
12. Admin can open Public Notice to publish a new notice.
13. Admin can open Create Requests to approve or reject pending resident account requests.
14. Admin menu contains Admin Profile, Create New User, Change Password, and Logout.

## 7. Resident Workflow

1. Resident logs in through Resident Login.
2. Resident lands on Resident Home.
3. Resident sees personal complaint summary and latest notices.
4. Resident opens Raise Complaint.
5. Resident enters category and description.
6. Resident optionally uploads an image.
7. System creates the complaint with default status Open and default priority Medium.
8. Resident opens My Complaints.
9. Resident sees only complaints created by their own account.
10. Resident opens a complaint detail page.
11. Resident sees current status, priority, deadline, image, and status history.
12. Resident opens Notices to view admin notices.
13. Resident opens Notifications to see unread and read notifications.
14. Resident uses My Profile to change password or logout.

## 8. Registration Request Workflow

1. New resident tries to log in through Resident Login.
2. If the email is not found, the app redirects to Send Create Request.
3. The form is prefilled with the attempted email.
4. Resident can edit name and email.
5. Resident submits the request.
6. System creates a `RegistrationRequest` with status Pending.
7. Admin opens Create Requests.
8. Admin reviews the name and email.
9. Admin clicks Create or Reject.
10. If Create, the system creates a resident user with an unusable password, stores the role in `Profile`, marks the request Approved, and sends a one-time password setup link.
11. If Reject, the system marks the request Rejected.

## 9. Complaint Status/History Dataflow

1. Resident submits complaint from `/complaints/new/`.
2. `ComplaintCreateForm` validates category, description, and optional image.
3. `Complaint` row is created with resident, category, description, image, `status=open`, and `priority=medium`.
4. Initial `ComplaintHistory` row is created with note `Complaint raised`.
5. Admin opens complaint detail page.
6. `ComplaintAdminUpdateForm` accepts priority, status, deadline, and note.
7. On save, old status is compared with new status.
8. If resolved, `resolved_at` is set.
9. `ComplaintHistory` stores actor, old status, new status, note, and timestamp.
10. `Notification` is created for the resident.
11. Email helper attempts to send complaint update email.

Overdue calculation happens in `Complaint.is_overdue`:

- Resolved complaints are never overdue.
- If a deadline exists and it is before today, the complaint is overdue.
- If no deadline exists, the complaint is overdue after `OVERDUE_DAYS`.

## 10. Notice/Email/Notification Dataflow

1. Admin opens Public Notice.
2. Admin enters title, body, and important flag.
3. `NoticeForm` validates input.
4. `Notice` row is created with `created_by`.
5. System finds all resident users.
6. For every resident, the system creates an in-app `Notification`.
7. If the notice is important, the system attempts to send email.
8. Notices are displayed with important notices pinned first.

Email is also used for account-created messages, complaint status update messages, and important notice messages. Email sending is intentionally wrapped so the main database action still succeeds if SMTP fails.

## 11. Image Upload Dataflow

1. Resident selects image while raising complaint.
2. Django receives the file through `request.FILES`.
3. `ComplaintCreateForm` validates the image field.
4. `Complaint.image` stores the uploaded file reference.
5. If `CLOUDINARY_URL` is configured, Django uses Cloudinary storage and uploads the image to Cloudinary.
6. If Cloudinary is not configured, Django stores images locally in `media/`.
7. Complaint detail template displays the image through `complaint.image.url`.

For Render deployment, Cloudinary should be configured because Render filesystem storage is not reliable for uploaded media.
