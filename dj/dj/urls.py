"""dj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin        # Probs dont need it
from django.urls import path, include


# This is the base url after the port number. http://127.0.0.1:8000/gate/{here is the url mentioned in dj_app.urls file}
# dj_app folder has to be in the same directory as manage.py only then it will be able to find the folder.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dj_app.urls'))            # the dot `.` is equivalent to `/` for directory
]   
