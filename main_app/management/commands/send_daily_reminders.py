# main_app/management/commands/send_daily_reminders.py
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from main_app.models import DailySanctuaryContent

# Dynamically fetch your custom AppUser model structure
User = get_user_model()


class Command(BaseCommand):
    help = "Dispatches scheduled daily reminders and card content summaries to opted-in users."

    def handle(self, *args, **options):
        # Determine the day number (clamped to 30 days maximum as requested)
        day_of_month = datetime.now().day
        if day_of_month > 30:
            day_of_month = 1

        # Fetch the day's content from the 30-day curriculum
        day_content = DailySanctuaryContent.objects.filter(
            day_number=day_of_month
        ).first()

        if not day_content:
            self.stdout.write(
                self.style.WARNING(
                    f"No admin context content found for Day {day_of_month}. Script halted."
                )
            )
            return

        # Target active users who explicitly opted in via wants_notifications
        opted_in_users = User.objects.filter(wants_notifications=True)

        sent_count = 0

        for user in opted_in_users:
            if not user.email:
                continue

            subject = f"Your Daily Sisterhood Reflection — Day {day_of_month} 🌸"
            message = (
                f"Good morning, Sis {user.username},\n\n"
                "Here is a small reminder to step away from the noise and log into your sanctuary space today.\n\n"
                f'✨ Today\'s Affirmation:\n"{day_content.daily_affirmation}"\n\n'
                "Come read your divine scripture guidance, check your wellness tips, and log your thoughts in your gratitude journal.\n\n"
                "Click here to enter your space: https://www.beyondsurvivalsisterhood.com/dashboard/\n\n"
                "Remember, you are never alone. Have a blessed day!"
            )

            try:
                # Dynamic sender configuration linked straight to Admin.bssr@gmail.com
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,  # Outputs exact mail tracebacks directly to your terminal log window
                )
                sent_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to dispatch notification to {user.email}: {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed and dispatched daily notifications for Day {day_of_month} to {sent_count} users."
            )
        )
