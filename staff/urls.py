from django.urls import path

from . import views

urlpatterns = [
    path("staff/", views.staff_list, name="staff-admin-list"),
    path("staff/new/", views.staff_create, name="staff-admin-create"),
    path("staff/<int:pk>/", views.staff_update, name="staff-admin-edit"),
    path("staff/<int:pk>/delete/", views.staff_delete, name="staff-admin-delete"),
    path("staff/<int:pk>/toggle/", views.staff_toggle_active, name="staff-admin-toggle"),
    path("staff/<int:pk>/move/<str:direction>/", views.staff_move, name="staff-admin-move"),
]