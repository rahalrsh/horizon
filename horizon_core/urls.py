"""
URL configuration for horizon_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.http import HttpResponse

# Google ads.txt
def ads_txt(request):
    content = "google.com, pub-1785022650944518, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('horizon.urls')),
    path('ads.txt', ads_txt),  # Serve ads.txt at the root
]
