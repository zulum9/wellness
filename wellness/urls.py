from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # This connects your main_app to the project
    # If you want the dashboard to be the homepage, leave the string empty ""
    path("", include("main_app.urls")),
    # Alternatively, if you wanted it at /app/dashboard, you'd use:
    # path("app/", include("main_app.urls")),
]
