from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentCard

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_card(sender, instance, created, **kwargs):
    if created:
        StudentCard.objects.get_or_create(user=instance)