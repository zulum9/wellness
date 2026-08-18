from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path


def sitemap_view(request):
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://beyond-survival-portal.onrender.com/</loc>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return HttpResponse(sitemap_xml, content_type="text/xml")


def manifest_view(request):
    manifest_data = {
        "name": "The Mindful Queen",
        "short_name": "MindfulQueen",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1e1015",
        "theme_color": "#1e1015",
        "icons": [
            {
                "src": "https://beyond-survival-portal.onrender.com/static/images/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": "https://beyond-survival-portal.onrender.com/static/images/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }
    return JsonResponse(manifest_data)


def assetlinks_view(request):
    assetlinks = [
        {
            "relation": ["delegate_permission/common.handle_all_urls"],
            "target": {
                "namespace": "android_app",
                "package_name": "com.mindfulqueen.app",
                "sha256_cert_fingerprints": [
                    "0F:DB:7E:DB:B4:30:4B:60:99:74:DA:DA:9D:61:8A:34:60:69:0B:3C:60:B8:CE:0C:FC:77:5C:11:C3:74:53:EE"
                ],
            },
        }
    ]
    return JsonResponse(assetlinks, safe=False)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap_view, name="sitemap"),
    path("manifest.json", manifest_view, name="manifest"),
    path(".well-known/assetlinks.json", assetlinks_view, name="assetlinks"),
    path("", include("main_app.urls")),  # Keep catch-all app include at the bottom
]
