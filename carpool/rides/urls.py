from django.urls import path
from . import views

app_name = 'rides'
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:ride_id>/", views.detail, name="detail"),
    path("add_ride", views.add_ride, name="add_ride"),
    path("request", views.request_ride, name="request_ride"),
    path("request/<int:request_id>", views.request_detail, name="request_detail"),
    path("request_cancel/<int:request_id>", views.request_cancel, name="request_cancel"),
    path("contact", views.contact, name="contact"),
    path("success", views.success, name="success"),
]