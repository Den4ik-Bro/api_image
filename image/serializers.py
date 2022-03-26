from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class UploadImageSerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    file = serializers.ImageField(required=False)

    def validate(self, attrs):
        if not self.validated_data['url'] and not self.validated_data['file']:
            raise serializers.ValidationError('no data for file upload')


class UpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('width', 'height')