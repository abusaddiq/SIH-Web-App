from django.urls import path

from . import views

dashboard_patterns = [
    path("", views.dashboard, name="prog-dash-home"),
    path("dashboard", views.dashboard, name="prog-dash-dashboard"),
    path("programmes/", views.programme_list, name="prog-dash-programmes"),
    path("programmes/new/", views.programme_create, name="prog-dash-programme-create"),
    path("programmes/<int:pk>/", views.programme_edit, name="prog-dash-programme-edit"),
    path("registrations/", views.registrations, name="prog-dash-registrations"),
    path("registrations/<int:pk>/", views.registration_update, name="prog-dash-registration-update"),
    path("enquiries/", views.enquiries, name="prog-dash-enquiries"),
    path("enquiries/<int:pk>/", views.enquiry_detail, name="prog-dash-enquiry-detail"),
    path("trainers/", views.trainers, name="prog-dash-trainers"),
    path("trainers/new/", views.trainer_create, name="prog-dash-trainer-create"),
    path("trainers/<int:pk>/", views.trainer_edit, name="prog-dash-trainer-edit"),
    path("trainers/<int:pk>/delete/", views.trainer_delete, name="prog-dash-trainer-delete"),
    path("categories/", views.categories, name="prog-dash-categories"),
]

urlpatterns = [
    path("", views.public_programmes, name="public-programmes"),
    path("training/", views.public_training, name="public-training"),
    path("<slug:slug>/", views.public_programme_detail, name="public-programme-detail"),
]