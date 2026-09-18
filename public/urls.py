from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="public-home"),
    path("about/", views.about, name="public-about"),
    path("team/", views.team, name="public-team"),
    path("services/", views.services, name="public-services"),
    path("projects/", views.projects, name="public-projects"),
    path("facilities/", views.facilities, name="public-facilities"),
    path("facilities/<slug:slug>/", views.facility_detail, name="public-facility-detail"),
    path("facilities/<slug:slug>/book/", views.facility_book, name="public-facility-book"),
    path("facilities/<slug:slug>/enquiry/", views.facility_enquiry, name="public-facility-enquiry"),
    path("meeting-rooms/", views.meeting_rooms, name="public-meeting-rooms"),
    path("contact/", views.contact, name="public-contact"),
    path("search/", views.search, name="public-search"),
    path("ai-chat/", views.ai_chat, name="public-ai-chat"),
    path("ai/ask/", views.ai_chat_ask, name="public-ai-ask"),
    path("pages/<slug>/", views.cms_page, name="public-cms-page"),
]