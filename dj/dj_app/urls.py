from django.urls import path
from . import views
# this file is within dj_app




urlpatterns = [
    path('', views.flight_info, name = 'flight_info'),   # Home page.
    path('flight_info', views.flight_info, name = 'flight_info'),
]