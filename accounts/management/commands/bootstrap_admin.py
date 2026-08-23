from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Profile


class Command(BaseCommand):
    help = "Create or update an admin login using email as username."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--name", default="Admin")

    def handle(self, *args, **options):
        email = options["email"].lower()
        first_name, _, last_name = options["name"].partition(" ")
        user, _ = User.objects.update_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password(options["password"])
        user.save()
        Profile.objects.update_or_create(user=user, defaults={"role": Profile.ADMIN})
        self.stdout.write(self.style.SUCCESS(f"Admin ready: {email}"))
