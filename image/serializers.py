from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ('picture', 'name', 'url', 'parent_picture')

    def validate(self, data):
        if 'width' not in data and 'height' not in data:
            raise serializers.ValidationError('no date given')
        if 'url' in data and 'file' in data:
            raise serializers.ValidationError('not an explicit file path')
        return data


class UploadImageSerializer(serializers.Serializer):
    url = serializers.URLField(required=False)
    file = serializers.ImageField(required=False)

    def validate(self, data):
        if 'url' not in data and 'file' not in data:
            raise serializers.ValidationError('no data for file upload')
        if 'url' in data and 'file' in data:
            raise serializers.ValidationError('not an explicit file path')
        return data


# class UpdateImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Image
#         fields = ('width', 'height')