# from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Ride, Passenger, RequestRide
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import datetime
from datetime import timedelta
from .forms import ContactForm

def bookRide(request, passenger, ride):
    #add the passenger to that ride
    passenger.rides.add(ride)
    #send confimation email to both riders and host
    send_mail(
        'Ride Confirmed',
        f'Your ride has been booked. The host is {ride.name.first_name} {ride.name.last_name}. Email: {ride.name.email}',
        'ride2luther@gmail.com',
        [f'{passenger.name.email}'],
        fail_silently=False,
    )
    send_mail(
        'Passenger Joined',
        f'A new passenger has joined your ride. Name: {passenger.name.first_name} {passenger.name.last_name}. Email: {passenger.name.email}',
        'ride2luther@gmail.com',
        [f'{ride.name.email}'],
        fail_silently=False,
    )
    
    return render(request, "rides/success.html" , {"host":ride.name.username, "ride":ride})

def index(request):
    # rides = Ride.objects.filter(date__gte==timezone.now())
    rides = Ride.objects.all()
    rides = rides.filter(date__gte=timezone.now())
    rides = rides.order_by('date')

    # order the rides by date ascending order


    requested_rides = RequestRide.objects.all()
    requested_rides = requested_rides.filter(date__gte=timezone.now())
    requested_rides = requested_rides.order_by('date')

    # order the rides by date ascending order


    # filter rides with seats_remaining > 0
    context = {
        "rides": rides,
        "now": timezone.now(),
        "loggedIn" : request.user.is_authenticated,
        "requested_rides": requested_rides,
    }
    return render(request, "rides/index.html", context)

@login_required(login_url='/users/')
def detail(request, ride_id):
    ride = Ride.objects.get(pk=ride_id)
    if request.method == 'POST':
        if request.user.username == ride.name.username:
            pickupDescription = request.POST.get('pickupDirections')
            ride.pickupDirections = pickupDescription
            ride.save()
            return redirect(f"/{ride_id}")
        else:
            seats_remaning = ride.seats - len(ride.passengers.all())
            # if the ride isn't fully booked already
            if seats_remaning >= 1:

                # get the authenticated user's username
                user = request.user
                username = user.username
                #check if the person giving ride is not the user (can't book a ride for himself) 
                if ride.name.username != username:
                    
                    # if that user is not yet a Passenger object, create one
                    passengerName = Passenger.objects.filter(name=user)
                    
                    if not passengerName:
                        #create a passenger with that username, book ride for the user
                        passenger = Passenger(name=user)
                        passenger.save()
                        
                        return bookRide(request, passenger, ride)
                    
                    else:
                        passenger = passengerName[0]
                        #check if the user is already not on the ride 
                        if ride not in passenger.rides.all():
                            #book ride for that user
                            return bookRide(request, passenger, ride)

                        else:
                            message = "You cannot book a ride twice"
                            return render(request, "rides/error.html", {"message":message})

                else:
                    message = "You cannot book a ride for yourself"
                    #redirect to error page
                    return render(request, "rides/error.html", {"message":message}) 

            else:
                #redirect with not success message
                message = "This ride is fully booked"
                return render(request, "rides/error.html", {"message":message}) 
    else:
        passengers = []
        for passenger in ride.passengers.all():
            passengers.append(passenger.name)
        
        context = {
            "ride": ride,
            "seats_remaining":ride.seats - len(ride.passengers.all()),
            "passengers": passengers,
            "user": request.user,
        }
        return render(request, "rides/detail.html", context)


def rideValid(origin, destination, date, seats):
    message = ''
    #check some error conditions 
    #error if origin and destination are same
    if origin == destination:
        message = "Origin and Destination cannot be same!"
    # error if trying to book for past date
        
    elif date < timezone.now().date():
        message = "You cannot add a ride for the past date"
    # error if booking for beyond 90 days
    elif date >  timezone.now().date() + timedelta(days=90):
        message = "New ride must be within 90 days relative to today."
    # error if number of seats is less than 1
    elif int(seats) <= 0:
        message = "Number of seats must be greater than 0"
    return message

@login_required(login_url='/users/')
def add_ride(request):
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        date = request.POST.get('date')
        time = request.POST.get('time')
        seats = request.POST.get('seats')
        name = request.user
        pickupDirections = request.POST.get('pickupDirections')
        message = ''
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        # check the lenght of fileds?
        #call the rideValid for check the validity of ride
        message = rideValid(origin, destination, date, seats)

        #if message is not '', it implies some error was triggered
        if message != '':
            return render(request, "rides/add_ride.html", {"message":message})
        else:
            # some input could be bad. so try to create a ride with the given data
            # display error if it is not possible
            try:
                newRide = Ride(origin=origin, destination=destination, date=date, time=time, seats=seats, name=name, pickupDirections=pickupDirections)
            except:
                return render(request, "rides/add_ride.html", {"message":"Invalid Entry. Please Try Again"})
            newRide.save()
            rideId = newRide.id
            return redirect(f"/{rideId}")
    else:
        return render(request, 'rides/add_ride.html')

def success(request):
    message = "Action performed successfully."
    return render(request, "rides/success.html", {"message":message})


@login_required(login_url='/users')
def request_cancel(request, request_id):
    if request.method == 'POST':
        #get the ride with request_id primary key
        ride_requested = RequestRide.objects.get(pk=request_id)
        #deleted the ride
        ride_requested.delete()
        # success message
        message = "The ride you requested has been successfully deleted."
        # render the success page
        return redirect("/success")
        # return render(request, "rides/success.html", {"message":message})

@login_required(login_url='/users')
def request_detail(request, request_id):
    try:
        request_ride = RequestRide.objects.get(pk=request_id)
    except:
        #no such requested ride exists
        return render(request, "rides/error.html", {"message":"No such requested ride."})        
    # POST method if someone wants to accept to give that ride.
    if request.method == "POST":
        # if someone wants to host that ride
        #get the description of the requested ride
        origin = request_ride.origin
        destination = request_ride.destination
        date = request_ride.date
        time = request.POST.get('time')
        seats = request.POST.get('seats')
        pickupDirections = request.POST.get('pickupDirections')
        # the host of the ride will be user providing the ride
        name = request.user 
        #check the validity of the ride
        message = rideValid(origin, destination, date, seats)
        # if no errors exist, try creating the ride
        if message == '':
            try:
                newRide = Ride(origin=origin, destination=destination, date=date, time=time, seats=seats, name=name, pickupDirections=pickupDirections)
            except:
                # return the error page
                return render(request, "rides/error.html", {"message":"Invalid Entry. Please Try Again Later"})            
            # delete that ride in the RequestRide table
            request_ride.delete()
            # add the ride to the Passenger who requested the ride
            newRide.save()
            passenger_user = request_ride.name
            #get the passenger with that username, if exists
            #if not create the passenger 
            try:
                passenger = Passenger.objects.filter(name=passenger_user)[0]
            except:
                passenger = Passenger(name=passenger_user)
                passenger.save()
            return bookRide(request, passenger, newRide)
        else:
            # render the error page displaying the error found by rideValid function.
            return render(request, "rides/error.html", {"message":message})
    else:
        # if the request isn't POST(i.e GET)
        #display the details for the requested ride.
        return render(request, "rides/request_detail.html", {"ride": request_ride, "user":request.user})

@login_required(login_url='/users/')
def request_ride(request):
    # page to request the ride a new ride
    # POST method to submit the details of requested ride
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        date = request.POST.get('date')
        timeConstraints = request.POST.get('timeConstraints')
        # time = request.POST.get('time')
        name = request.user
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        #buch of conditions to be checked for the validity of the Ride.
        #call the rideValid for check the validity of ride
        message = rideValid(origin, destination, date, seats=1)
        try:
            requestedRide = RequestRide(origin=origin, destination=destination, date=date, time=timeConstraints, name=name)
        except:
            message = "There is some error in the input. Please fill it out again."
            return render(request, "rides/request.html", {"message":message})
        requestedRide.save()
        requestId = requestedRide.id
        return redirect(f"/request/{requestId}")
    else:
        #GET method to display the form to request the ride
        return render(request, "rides/request.html")
    
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                name = request.user.username
                name = name + '@luther.edu'
            else:
                name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            send_mail(
                'Contact Form RS Luther',
                f'Name: {name} Message: {message}',
                'ride2luther@gmail.com',
                ['ride2luther@gmail.com'],
                fail_silently=False,
            )
            return render(request, "rides/success.html", {"message":"Your enquiry has been successfully submitted. We will get back to you soon."})
    form = ContactForm()
    return render(request, "rides/contact.html", {"form":form, "loggedIn":request.user.is_authenticated})        