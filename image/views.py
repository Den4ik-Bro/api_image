import datetime
import os
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Image as ImageModel
from .serializers import ImageSerializer, UploadImageSerializer
from PIL import Image
import requests
from hashlib import md5


class ImageViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            if 'file' in serializer.validated_data and serializer.validated_data['file']:
                file = serializer.validated_data['file']
                filename = file
                image = Image.open(file)
                url = None
            else:
                url = serializer.validated_data['url']
                result = requests.get(url=url, stream=True)
                if result.status_code == 200:
                    filename = url.split('/')[-1]
                    hash = md5(filename.encode() + str(datetime.datetime.now()).encode()).hexdigest()
                    filename = f'picture/{hash}.jpg'
                    file = open(f'media/{filename}', 'wb')
                    file.write(result.content)
                    file.close()
                    image = Image.open(file.name)
                else:
                    return Response({"error": "unable to upload image: wrong url"})
            picture = ImageModel.objects.create(
                picture=filename,
                name=file.name.split('/')[-1],
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
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            size = (serializer.validated_data['width'], serializer.validated_data['height'])
            image = Image.open(f'media/{str(instance.picture)}')
            new_image = image.resize(size)
            new_filename = f'picture/update{str(instance.name)}_{size[0]}x{size[1]}.jpg'
            new_image.save(f'media/{new_filename}')
            new_instance = ImageModel.objects.create(
                picture=new_filename,
                name=f'update{str(instance.name)}_{size[0]}x{size[1]}.jpg',
                width=size[0],
                height=size[1],
                parent_picture=instance
            )
            return Response(self.serializer_class(new_instance).data, status.HTTP_201_CREATED)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = super().get_object()
        instance.descendants.clear()
        if os.path.exists(instance.picture.path):
            os.remove(instance.picture.path)
        return super().destroy(request, *args, **kwargs)