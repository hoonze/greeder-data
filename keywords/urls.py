from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from keywords import views

urlpatterns = [
    path('keyword_extraction', views.extraction),
]

urlpatterns = format_suffix_patterns(urlpatterns)
