from django.urls import path

from . import views

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
]
