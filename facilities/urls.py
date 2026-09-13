from django.urls import path

from . import views

urlpatterns = [
    path("facilities/", views.facilities_list, name="fac-admin-facilities"),
    path("facilities/new/", views.facility_create, name="fac-admin-facility-create"),
    path("facilities/<int:pk>/", views.facility_update, name="fac-admin-facility-edit"),
    path("facilities/<int:pk>/delete/", views.facility_delete, name="fac-admin-facility-delete"),
    path("facilities/<int:pk>/prices/", views.facility_prices, name="fac-admin-prices"),
    path("facilities/<int:pk>/images/", views.facility_images, name="fac-admin-facility-images"),
    path("facilities/images/<int:pk>/", views.facility_image_edit, name="fac-admin-facility-image-edit"),
    path("facilities/images/<int:pk>/delete/", views.facility_image_delete, name="fac-admin-facility-image-delete"),
    path("facilities/images/<int:pk>/up/", views.facility_image_up, name="fac-admin-facility-image-up"),
    path("facilities/images/<int:pk>/down/", views.facility_image_down, name="fac-admin-facility-image-down"),
    path("facilities/images/<int:pk>/primary/", views.facility_image_set_primary, name="fac-admin-facility-image-primary"),
    path("prices/<int:pk>/delete/", views.facility_price_delete, name="fac-admin-price-delete"),
    path("facility-categories/", views.facility_categories, name="fac-admin-categories"),
    path("services/", views.services_list, name="fac-admin-services"),
    path("services/new/", views.service_create, name="fac-admin-service-create"),
    path("services/<int:pk>/", views.service_update, name="fac-admin-service-edit"),
    path("services/<int:pk>/delete/", views.service_delete, name="fac-admin-service-delete"),
    path("bookings/", views.bookings_list, name="fac-admin-bookings"),
    path("bookings/<int:pk>/", views.booking_detail, name="fac-admin-booking-detail"),
    path("enquiries/", views.enquiries_list, name="fac-admin-enquiries"),
    path("enquiries/<int:pk>/", views.enquiry_detail, name="fac-admin-enquiry-detail"),
]