from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    AppUser,
    DailySanctuaryContent,
    DailyUplift,
    GratitudeThought,
    SupportGroup,
)


# Register your custom AppUser model so you can manage users in the admin panel
@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    # This extends the default User admin to show your custom fields
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Profile Info", {"fields": ("age", "country", "wants_notifications")}),
    )
    list_display = ("username", "email", "country", "wants_notifications", "is_staff")


# Register the 30-Day Calendar Dictionary
@admin.register(DailySanctuaryContent)
class DailySanctuaryContentAdmin(admin.ModelAdmin):
    list_display = ("day_number", "divine_guidance", "daily_affirmation")
    ordering = ("day_number",)


# Register the remaining models
admin.site.register(DailyUplift)
admin.site.register(GratitudeThought)
admin.site.register(SupportGroup)
