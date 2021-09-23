from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from keywords import views

urlpatterns = [
    path('keywords/', views.extraction),
]

urlpatterns = format_suffix_patterns(urlpatterns)
