# Society Maintenance Tracker - Complete Setup And Deployment Guide

This file is the practical step-by-step guide for running the project locally and deploying the whole application on Render.

The project uses Django, PostgreSQL, Cloudinary, Gmail SMTP, and Render.

## 0. What You Need Before Starting

Create or prepare these accounts:

- GitHub account
- Render account
- Cloudinary account
- Gmail account with 2-Step Verification enabled

Install these locally:

- Python 3.10 or newer
- Git
- A code editor

Do not upload or share `.env`. It contains passwords and API keys.

## 1. Important Project Files

| File | Responsibility |
| --- | --- |
| `.env` | Your real local secrets. Never commit this. |
| `.env.example` | Example env file for documentation. Safe to commit. |
| `requirements.txt` | Python packages Render installs. |
| `render.yaml` | Optional Render Blueprint config. |
| `manage.py` | Django command runner. |
| `society_tracker/settings.py` | Reads env variables and configures database, email, Cloudinary, and static files. |
| `README.md` | Main project explanation. |
| `SETUP.md` | Setup and deployment guide. |

## 2. Create A Virtual Environment

From the project folder:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

The `.venv` folder should not be committed to GitHub.

## 3. Create The `.env` File

Copy the example:

```powershell
copy .env.example .env
```

Then edit `.env` with real values.

Final local `.env` should look like this:

```env
SECRET_KEY=your-real-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=your-render-postgres-external-url
OVERDUE_DAYS=4
CLOUDINARY_URL=cloudinary://your_api_key:your_api_secret@your_cloud_name
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=Society Tracker <yourgmail@gmail.com>
```

## 4. Generate Django `SECRET_KEY`

Run:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output into `.env`:

```env
SECRET_KEY=paste-the-generated-key-here
```

Never use `SECRET_KEY=change-me` for deployment.

## 5. PostgreSQL Setup With Render

1. Go to Render Dashboard.
2. Click New.
3. Choose PostgreSQL.
4. Create a database, for example `society-maintenance-db`.
5. Open the database Info page.

Render gives two database URLs:

| URL | Use |
| --- | --- |
| External Database URL | Use locally from your laptop. |
| Internal Database URL | Use inside Render web service. |

For local testing, put the External Database URL in `.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME
```

This project uses `load_dotenv(..., override=True)`, so `.env` overrides old system-level env values after the server restarts.

Apply migrations:

```powershell
python manage.py migrate
```

Confirm migrations:

```powershell
python manage.py showmigrations --plan
```

Every migration should show `[X]`.

## 6. Cloudinary Setup

Cloudinary stores complaint images. This is required for hosted deployment because Render does not permanently store uploaded files on disk.

1. Create a Cloudinary account.
2. Open Cloudinary Dashboard.
3. Copy Cloud name, API key, and API secret.
4. Build this value:

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

Common wrong value:

```env
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

That is only a placeholder. If you leave `api_key` literally in the URL, uploads fail with `Invalid api_key api_key`.

After setting Cloudinary, test by raising a complaint with an image.

## 7. Gmail SMTP Setup

The app sends emails for account creation, complaint status changes, and important notices.

Get Gmail App Password:

1. Open `https://myaccount.google.com/security`.
2. Turn on 2-Step Verification.
3. Open `https://myaccount.google.com/apppasswords`.
4. Create an app password named `Django Society Tracker`.
5. Google gives a 16-character password.
6. Paste it into `.env` without spaces.

Gmail `.env` values:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your16characterapppassword
DEFAULT_FROM_EMAIL=Society Tracker <yourgmail@gmail.com>
```

Do not use your normal Gmail password.

Test Gmail SMTP:

```powershell
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','society_tracker.settings'); import django; django.setup(); from django.core.mail import send_mail; from django.conf import settings; print(send_mail('Society Tracker test','Mail is working.', settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], fail_silently=False))"
```

Expected output:

```text
1
```

## 8. Create First Admin

After migrations:

```powershell
python manage.py bootstrap_admin --email admin@example.com --password admin123 --name "Society Admin"
```

For final submission, use your real email and a stronger password:

```powershell
python manage.py bootstrap_admin --email yourgmail@gmail.com --password YourStrongPassword --name "Society Admin"
```

This creates an admin in whichever database `DATABASE_URL` points to.

## 9. Run Locally With Render PostgreSQL, Cloudinary, And Gmail

Start the server:

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/login/
```

Test this complete local flow:

1. Login as admin.
2. Create resident.
3. Confirm resident account-created email arrives.
4. Logout.
5. Login as resident.
6. Raise complaint with image.
7. Confirm image uploads and complaint appears in My Complaints.
8. Logout.
9. Login as admin.
10. Open Manage Complaints.
11. Update complaint status and note.
12. Confirm resident receives email.
13. Publish important notice.
14. Confirm residents receive email.

## 10. Run Automated Tests Safely

Use `TEST_DATABASE_URL` so tests do not touch Render PostgreSQL:

```powershell
$env:TEST_DATABASE_URL='sqlite:///:memory:'
python manage.py test
```

Expected result:

```text
OK
```

Do not run tests directly against your Render production database.

## 11. Prepare GitHub Repository

Before pushing:

```powershell
git status --short
```

Make sure these files are not staged:

- `.env`
- `.venv/`
- `db.sqlite3`
- `media/`
- `staticfiles/`

Initialize and push:

```powershell
git init
git add .
git commit -m "Initial society maintenance tracker"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

## 12. Deploy The Whole Application On Render

If you already created PostgreSQL, create only the web application.

Manual Web Service steps:

1. Render Dashboard.
2. New.
3. Web Service.
4. Connect GitHub repository.
5. Environment: Python.
6. Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

7. Start command:

```bash
gunicorn society_tracker.wsgi:application
```

8. Add environment variables from the next section.
9. Click Deploy.

The project also has `render.yaml` for Blueprint deployment. If the database already exists manually, the manual Web Service path is usually clearer.

## 13. Render Environment Variables

In Render Web Service, add:

```env
SECRET_KEY=your-real-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-service-name.onrender.com,.onrender.com
DATABASE_URL=your-render-internal-database-url
OVERDUE_DAYS=4
CLOUDINARY_URL=cloudinary://your_api_key:your_api_secret@your_cloud_name
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourgmail@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=Society Tracker <yourgmail@gmail.com>
```

Important:

- Use `DEBUG=False` on Render.
- Use Render PostgreSQL Internal Database URL on Render.
- Use Render PostgreSQL External Database URL locally.
- Do not put quotes around env values in Render.

## 14. After Render Deploys

Open Render service logs. Confirm:

- dependencies installed,
- static files collected,
- migrations applied,
- Gunicorn started successfully.

Then create or reset admin in Render Shell:

```bash
python manage.py bootstrap_admin --email yourgmail@gmail.com --password YourStrongPassword --name "Society Admin"
```

Open hosted URL:

```text
https://your-service-name.onrender.com/login/
```

Login through Admin Login.

## 15. Final Hosted Testing Checklist

Test these on the Render URL:

- Admin login works.
- Admin dashboard loads.
- Admin can create resident.
- Resident receives account-created email.
- Resident login works.
- Resident can raise complaint without image.
- Resident can raise complaint with image.
- Uploaded image displays from Cloudinary.
- Resident sees complaint in My Complaints.
- Admin sees complaint in Manage Complaints.
- Admin can update priority/status/deadline/note.
- Resident receives complaint status email.
- Admin can publish important notice.
- Resident receives notice email.
- Admin can delete notice.
- Notifications page shows in-app notifications.
- Light/dark mode works.

## 16. Common Errors And Fixes

### `Invalid api_key api_key`

Cause: `CLOUDINARY_URL` still has placeholder `api_key`.

Fix: replace with the real Cloudinary API key.

### Email does not send

Check:

- `EMAIL_HOST=smtp.gmail.com`
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER` is your Gmail address
- `EMAIL_HOST_PASSWORD` is Google App Password, not normal password
- `DEFAULT_FROM_EMAIL=Society Tracker <same-gmail-address>`

### Django still uses an old database URL

Cause: system-level `DATABASE_URL` existed before `.env`.

Fix: restart the server. This project uses `load_dotenv(..., override=True)` so `.env` wins after restart.

### Render says `DisallowedHost`

Fix:

```env
ALLOWED_HOSTS=your-service-name.onrender.com,.onrender.com
```

### Static files missing on Render

Confirm build command includes:

```bash
python manage.py collectstatic --noinput
```

### Uploaded images disappear on Render

Cause: local media storage used instead of Cloudinary.

Fix: set `CLOUDINARY_URL` in Render environment variables.

## 17. Production And Security Notes

- Never commit `.env`.
- Never commit `.venv`.
- Never commit `db.sqlite3`.
- Never commit uploaded media.
- Keep `DEBUG=False` on Render.
- Rotate secrets if screenshots exposed them.
- Use a strong admin password.
- Use Gmail App Password, not normal Gmail password.
- Render PostgreSQL credentials should stay private.
- Cloudinary API secret should stay private.
- The assignment workflow stores requested passwords in `RegistrationRequest`. This is acceptable for the requested demo workflow, but production systems should use invite links or password reset links instead.
- Email failures are non-blocking in the app; database records and in-app notifications still get created.

## 18. Final Submission Items

Submit:

- GitHub repository link.
- Render hosted URL.
- Admin login credentials for evaluator.
- `README.md`.
- `SETUP.md`.
- `SYSTEM_DESIGN.md`.

Before submitting, verify the hosted app using the checklist in section 15.
