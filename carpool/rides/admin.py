from django.contrib import admin

from .models import Ride, Passenger
# Register your models here.

class PassengerAdmin(admin.ModelAdmin):
    filter_horizontal = ("rides",)

admin.site.register(Ride)

admin.site.register(Passenger, PassengerAdmin)
