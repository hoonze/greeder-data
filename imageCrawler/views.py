from django.shortcuts import render
from .models import Image
from .serializers import ImageSerializer
from rest_framework import viewsets


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class =ImageSerializer

    # def get(self, request):
    #     # 여러개의 객체를 serialization하기 위해 many = True로 설정
    #     return self.list(request)

    # def post(self, request):
    #     return self.create(request)
