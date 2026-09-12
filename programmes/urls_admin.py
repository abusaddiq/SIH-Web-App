from django.urls import path

from . import views

urlpatterns = [
    path("programmes/", views.admin_programmes, name="prog-admin-list"),
    path("programmes/<int:pk>/", views.admin_programme_detail, name="prog-admin-detail"),
]