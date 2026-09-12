from django.urls import path

from . import views
from . import cms_views

urlpatterns = [
    path("", views.admin_dashboard_view, name="core-dashboard"),
    path("dashboard", views.admin_dashboard_view, name="core-dashboard-alt"),
    path("settings/site/", views.site_settings_view, name="core-site-settings"),
    path("settings/contact/", views.contact_settings_view, name="core-contact-settings"),
    path("settings/homepage/", views.homepage_sections_view, name="core-homepage-sections"),
    path("settings/homepage/<slug>/", views.homepage_section_detail_view, name="core-homepage-section-edit"),
    path("settings/pages/", cms_views.pages_list, name="core-pages-list"),
    path("settings/pages/new/", cms_views.page_create, name="core-page-create"),
    path("settings/pages/<int:pk>/", cms_views.page_edit, name="core-page-edit"),
    path("settings/pages/<int:pk>/delete/", cms_views.page_delete, name="core-page-delete"),
    path("media/", views.media_library_view, name="core-media"),
    path("media/<int:pk>/", views.media_edit_view, name="core-media-edit"),
    path("media/<int:pk>/delete/", views.media_delete_view, name="core-media-delete"),
    path("audit-logs/", views.audit_logs_view, name="core-audit-logs"),
    path("notifications/", views.notifications_view, name="core-notifications"),
    path("notifications/<int:pk>/read/", views.notifications_mark_read, name="core-notification-read"),
    path("notifications/read-all/", views.notifications_mark_all, name="core-notification-read-all"),
]