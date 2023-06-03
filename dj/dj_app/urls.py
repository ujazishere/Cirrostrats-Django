from django.urls import path
from . import views
# this file is within dj_app




urlpatterns = [
    path('', views.home, name = 'home'),   # Home page.
    path('about', views.about, name = 'about'),   # about page.
    path('contact', views.contact, name = 'contact'),   # contact page.
    path('gate_info', views.gate_info, name = 'gate_info'),
    path('source', views.source, name = 'source'), #source page.
    path('gate_check', views.source, name = 'gate_check'), #gate_check page.
    path('flight_lookup', views.source, name = 'flight_lookup'), #flight_lookup page.
    path('weather', views.source, name = 'weather'), #weather page.  
]

