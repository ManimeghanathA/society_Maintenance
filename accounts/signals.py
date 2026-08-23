from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def ensure_profile_for_staff(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        Profile.objects.get_or_create(user=instance, defaults={"role": Profile.ADMIN})
