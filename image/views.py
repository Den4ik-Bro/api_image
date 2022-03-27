import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import Image as ImageModel
from .serializers import ImageSerializer, UploadImageSerializer, UpdateImageSerializer
from PIL import Image
import requests
from hashlib import md5


class ImageViewSet(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            if 'file' in serializer.validated_data and serializer.validated_data['file']:
                file = serializer.validated_data['file']
                filename = file
                image = Image.open(filename)
                picture = ImageModel.objects.create(
                    picture=filename,
                    name=filename,
                    width=image.size[0],
                    height=image.size[1],
                )
            else:
                url = serializer.validated_data['url']
                result = requests.get(url=url, stream=True)
                if result.status_code == 200:
                    filename = url.split('/')[-1]
                    hash = md5(filename.encode() + str(datetime.datetime.now()).encode()).hexdigest()
                    file = open(f'media/picture/{hash}.jpg', 'wb')
                    file.write(result.content)
                    file.close()
                image = Image.open(file.name)
                picture = ImageModel.objects.create(
                    picture=f'media/picture/{hash}.jpg',
                    name=hash,
                    url=url,
                    width=image.size[0],
                    height=image.size[1],
                )
            image_data = self.serializer_class(picture).data
            return Response(image_data, status.HTTP_201_CREATED)
        return Response(serializer.errors)

    @action(detail=True, methods=['post'])
    def resize(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateImageSerializer(data=request.data)
        if serializer.is_valid():
            size = (serializer.validated_data['width'], serializer.validated_data['height'])
            if not instance.url:
                print(instance.picture)
                image = Image.open(f'media/{str(instance.picture)}')
                new_image = image.resize(size)
                new_image.save(f'media/picture/update{str(instance.name)}.jpg')
                new_instance = ImageModel.objects.create(
                    picture=f'media/picture/update{str(instance.name)}.jpg',
                    name=f'update{str(instance.name)}.jpg',
                    width=size[0],
                    height=size[1],
                    parent_picture=instance
                )
            else:
                image = Image.open(str(instance.picture))
                new_image = image.resize(size)
                new_image.save(f'media/picture/update{str(instance.name)}.jpg')
                new_instance = ImageModel.objects.create(
                    picture=f'picture/update{str(instance.name)}.jpg',
                    name=f'update{str(instance.name)}.jpg',
                    url=instance.url,
                    width=size[0],
                    height=size[1],
                    parent_picture=instance
                )
            return Response(self.serializer_class(new_instance).data, status.HTTP_201_CREATED)
        return Response(serializer.errors)
