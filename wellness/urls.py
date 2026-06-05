from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView


# This function writes the sitemap automatically without needing a file!
def sitemap_view(request):
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://beyond-survival-portal.onrender.com/</loc>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return HttpResponse(sitemap_xml, content_type="text/xml")


urlpatterns = [
    path("admin/", admin.site.urls),
    # This connects your main_app to the project
    # If you want the dashboard to be the homepage, leave the string empty ""
    path("sitemap.xml", sitemap_view, name="sitemap"),
    path("", include("main_app.urls")),
    # Alternatively, if you wanted it at /app/dashboard, you'd use:
    # path("app/", include("main_app.urls")),
]
