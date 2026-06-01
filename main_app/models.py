from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField


# 1. Custom User Model handling all specific user details
class AppUser(AbstractUser):
    age = models.PositiveIntegerField(null=True, blank=True)
    country = CountryField()
    wants_notifications = models.BooleanField(
        default=False,
        help_text="True if the user opts in to receive daily reminder emails.",
    )

    # Overridden relations to fix custom auth user initialization errors (E304)
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="appuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="appuser_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.email if self.email else self.username


# 2. Fixed 30-Day Context Calendar (Loaded by Admin)
class DailySanctuaryContent(models.Model):
    day_number = models.PositiveIntegerField(
        unique=True,
        help_text="Day of the month (1 to 30) for this specific content set.",
    )
    divine_guidance = models.TextField(
        help_text="Scripture text & peace message loaded by admin."
    )
    daily_affirmation = models.TextField(
        help_text="The 'Sis, You Are...' affirmation text."
    )
    wellness_tip = models.TextField(help_text="Nourish wellness tip.")
    gratitude_prompt = models.TextField(
        help_text="Today's prompt for the reflection journal."
    )
    daily_intention = models.TextField(help_text="The 'Today I Choose...' text.")

    class Meta:
        verbose_name = "Daily Sanctuary Content"
        verbose_name_plural = "Daily Sanctuary Content Calendar"
        ordering = ["day_number"]

    def __str__(self):
        return f"Sanctuary Dataset - Day {self.day_number}"


# 3. Structural Day of Week Features
class DailyUplift(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    day_of_week = models.IntegerField(choices=DAY_CHOICES, unique=True)
    word_of_day = models.CharField(max_length=100)
    inspiration_quote = models.TextField()
    mantra = models.TextField()
    featured_resource_link = models.URLField(blank=True)

    def __str__(self):
        return self.get_day_of_week_display()


# 4. User Interaction Tables
class GratitudeThought(models.Model):
    # Points cleanly to your active custom AppUser
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prompt = models.CharField(max_length=500)
    thought = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Shows newest thoughts first


class SupportGroup(models.Model):
    name = models.CharField(max_length=100)
    members_count = models.IntegerField(default=0)
    icon_name = models.CharField(
        max_length=50,
        help_text="Emoji or Material Icon descriptor name (e.g., '✨', '🌱', '🤝')",
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
