from django.shortcuts import render
from .models import Image
from .serializers import ImageSerializer
from rest_framework import viewsets

# Create your views here.
# controller + service

class ImageCrawler_main(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer