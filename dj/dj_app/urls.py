from django.urls import path
from . import views

urlpatterns = [
    # path('gate_out/united', views.gate_out, name = 'gate_out'),
    path('flight_info', views.flight_info, name = 'flight_info')
]