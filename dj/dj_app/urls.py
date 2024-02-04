from django.urls import path
from . import views
# this file is within dj_app
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path('', views.home, name = 'home'),   # Home page.
    path('ourstory', views.ourstory, name = 'ourstory'),   # about page.
    path('contact', views.contact, name = 'contact'),   # contact page.
    path('gate_info', views.gate_info, name = 'gate_info'),
    path('source', views.source, name = 'source'), #source page.
    path('gate_check', views.gate_check, name = 'gate_check'), #gate_check page.
    path('flight_lookup', views.flight_lookup, name = 'flight_lookup'), #flight_lookup page.
    path('weather', views.weather, name = 'weather'), #weather page. 
    path('guide', views.guide, name = 'guide'), #guide page. 
    path('report', views.report_an_issue, name = 'report'), #report page.
    path('live_map', views.live_map, name = 'live_map'), #live_map page.
    
    path('dummy2', views.dummy2, name = 'dummy2'), #  Main Page
    
    # This page is a views function that is loaded asynchronously after dummy2 loads up.
    # the string airport is passed as second argument to the data_v function in views.py
    path('data_v/<str:airport>/', views.data_v, name = 'data_v'),    

 
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)