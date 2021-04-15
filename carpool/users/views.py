from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from rides.models import Ride, Passenger
from django.utils import timezone



def login_page(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #if the url to go next was submitted, redirect to that url otherwise redirect to index
            
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("rides:index")
        else:
            return render(request, "users/login.html", {"message":"Invalid Credentails"})
    else:
        # don't take the user to login page if the user is already logged in
        if request.user.is_authenticated:
            return redirect("rides:index")
        else:
            # render the login page
            return render(request, "users/login.html", {"message":None})

def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {"message":"Logged out."})

@login_required(login_url='/users/')
def my_rides(request):
    user = request.user
    passenger = Passenger.objects.filter(name=user)[0]
    hosted_rides = Ride.objects.filter(name=user)
    hosted_rides = hosted_rides.filter(date__gte=timezone.now())
    hosted_rides = hosted_rides.order_by('date')
    taken_rides = passenger.rides.all()
    taken_rides = taken_rides.filter(date__gte=timezone.now())
    taken_rides = taken_rides.order_by('date')
    context = {
        "hosted":hosted_rides,
        "taken": taken_rides,
        "user":user
    }
    return render(request, "users/my_rides.html", context)

