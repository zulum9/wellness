from django.urls import path

from . import views
from .views import manifest_view, privacy_policy_view, account_deletion_view

urlpatterns = [
    path("", views.index, name="index"),  # Land here first!
    path("dashboard/", views.dashboard_view, name="dashboard"),  # Move this here
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    # FIX: Changed 'groups_view' to 'groups' to match your template error
    path("groups/", views.groups_view, name="groups"),
    # FIX: Ensure this path matches the JS fetch exactly
    path("api/explain/", views.fetch_explanation, name="fetch_explanation"),
    path("chatbot-response/", views.chatbot_response, name="chatbot_response"),
    path("logout/", views.logout_view, name="logout"),
    path("groups/", views.groups_view, name="groups"),
    path("manifest.json", manifest_view, name="manifest"),
    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),
    path('delete-account/', account_deletion_view, name='account_deletion'),
]
