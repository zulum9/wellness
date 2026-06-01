# main_app/signals.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


# Look for this exact function name from your traceback error log
@receiver(post_save, sender=User)
def handle_user_signup2(sender, instance, created, **kwargs):
    if created:
        subject = "Welcome to Beyond Survival Sisterhood! 🤍"
        message = (
            f"Hi {instance.username},\n\n"
            "Thank you for signing up to the Beyond Survival Sisterhood portal."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]

        # THE CRUCIAL CHANGE: Change fail_silently from False to True
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)
