from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User

# Create your models here.
class Ride(models.Model):
    origin = models.CharField(max_length=64)
    destination = models.CharField(max_length=64)
    date = models.DateField()
    time = models.TimeField()
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    seats=models.IntegerField(default=1)
    pickupDirections = models.CharField(max_length=200, default='')

    def __str__(self):
        return f"{self.origin}-{self.destination}:{self.date} at {self.time}"

class Passenger(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    rides = models.ManyToManyField(Ride, blank=True, related_name="passengers")
    
    def __str__(self):
        return f"{self.name}"

class RequestRide(models.Model):
    origin = models.CharField(max_length=64)
    destination = models.CharField(max_length=64)
    date = models.DateField()
    time = models.CharField(max_length=200)
    name = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Requested from {self.origin} to {self.destination} for {self.date} at {self.time}"