from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'keyword', 'desc', 'url') # JSON 파일에 보여질 필드를 선택