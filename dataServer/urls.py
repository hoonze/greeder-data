
from django.contrib import admin
from django.urls import path, include
from crawler import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crawler.urls')),
]
