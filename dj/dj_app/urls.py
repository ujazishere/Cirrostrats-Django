from django.urls import path
from . import views
# this file is within dj_app




urlpatterns = [
    path('', views.home, name = 'home'),   # Home page.
    # path('home', views.home, name = 'home'),   # Home page.
    path('about', views.about, name = 'about'),   # about page.
    path('contact', views.contact, name = 'contact'),   # contact page.
    path('gate_info', views.gate_info, name = 'gate_info'),
]