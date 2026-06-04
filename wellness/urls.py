from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    # This connects your main_app to the project
    # If you want the dashboard to be the homepage, leave the string empty ""
    path("", include("main_app.urls")),
    path(
        "sitemap.xml",
        TemplateView.as_view(
            template_name="sitemap.xml", content_type="application/xml"
        ),
    ),
    # Alternatively, if you wanted it at /app/dashboard, you'd use:
    # path("app/", include("main_app.urls")),
]
