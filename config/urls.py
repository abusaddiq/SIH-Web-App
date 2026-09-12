from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

from blog.models import Post
from facilities.models import Facility
from programmes.models import Programme
from core.models import CmsPage

admin.autodiscover()


def robots_txt(request):
    lines = ["User-agent: *"]
    lines.append("Disallow:" if settings.DEBUG else "Allow: /")
    if not settings.DEBUG:
        lines.append("\nSitemap: https://%s/sitemap.xml" % request.get_host())
    return HttpResponse("\n".join(lines), content_type="text/plain")


class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return ["/", "/about/", "/services/", "/facilities/", "/programmes/", "/blog/", "/contact/", "/ai-chat/"]

    def location(self, item):
        return item


class FacilitySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Facility.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class ProgrammeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Programme.objects.filter(status="published")


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class CMSSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.4

    def items(self):
        return CmsPage.objects.filter(is_published=True)

    def location(self, obj):
        return f"/pages/{obj.slug}/"


sitemaps = {
    "static": StaticSitemap,
    "facilities": FacilitySitemap,
    "programmes": ProgrammeSitemap,
    "posts": PostSitemap,
    "pages": CMSSitemap,
}

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", include("public.urls")),
    path("blog/", include("blog.urls")),
    path("programmes/", include("programmes.urls")),
    path("admin/", include("facilities.urls")),
    path("admin/", include("blog.urls_admin")),
    path("admin/", include("programmes.urls_admin")),
    path("admin/", include("core.urls")),
    path("content-dashboard/", include("blog.urls_content")),
    path("programmes-dashboard/", include("programmes.dashboard_urls")),
    path("robots.txt", robots_txt),
    path(
        "sitemap.xml",
        sitemap_views.index,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )