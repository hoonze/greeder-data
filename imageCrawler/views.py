from django.shortcuts import render
from rest_framework import response
from .models import Image
from .serializers import ImageSerializer

# APIView를 사용하기 위해 import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class ImageAPI(APIView):
    def get(self, request):
        images = Image.objects.all()
        # 여러개의 객체를 serialization하기 위해 many = True로 설정
        serializer = ImageSerializer(images, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ImageSerializer(data=request.data)

        if serializer.is_valid():  # 유효성 검사
            serializer.save()  # 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
