
from django.urls import path
# from rest_framework import routers
# from django.middleware.Cor
from . import route
from django.conf import settings


"""
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('weather',views.weather_display)
"""


urlpatterns = [
    path('', route.home, name='home'),   # Home page.
    # path('api/react_dummy', views.react_dummy, name='react_dummy'),   # Home page.
    path('ourstory', route.ourstory, name='ourstory'),   # about page.
    path('contact', route.contact, name='contact'),   # contact page.
    path('gate_info', route.gate_info, name='gate_info'),
    path('source', route.source, name='source'),  # source page.
    # gate_check page.
    path('gate_check', route.gate_check, name='gate_check'),
    # flight_lookup page.
    path('flight_lookup', route.flight_lookup, name='flight_lookup'),
    path('weather', route.weather, name='weather'),  # weather page.
    path('guide', route.guide, name='guide'),  # guide page.
    path('report', route.report_an_issue, name='report'),  # report page.
    path('live_map', route.live_map, name='live_map'),  # live_map page.

    path('extra_dummy', route.extra_dummy, name='extra_dummy'),  # Main Page

    # This page is a views function that is loaded asynchronously after dummy2 loads up.
    # the string airport is passed as second argument to the nas_data and subsequent functions in views.py
    path('nas_data/<str:airport>/', route.nas_data, name='nas_data'),
    path('data_v/<str:airport>/', route.data_v, name='data_v'),
    path('weather_data/<str:airport>/',
         route.weather_data, name='weather_data_name'),
    path('summary_box/<str:airport>/', route.summary_box, name='summary_box'),
]


# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
