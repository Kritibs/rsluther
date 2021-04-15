from . import views
from  django.urls import path

app_name = "users"
urlpatterns = [
    path("", views.login_page, name="login"),
    path("logout", views.logout_view, name="logout"), 
    path("myrides",views.my_rides, name="my_rides"),
]
