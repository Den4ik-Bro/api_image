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
        if request.data.get('file') != None:
            file = request.data['file']
            image = Image.open(file)
            picture = ImageModel.objects.create(
                picture=file,
                name=file.name,
                width=image.size[0],
                height=image.size[1],
            )
        else:
            result = requests.get(url=request.data['url'], stream=True)
            if result.status_code == 200:
                filename = request.data['url'].split('/')[-1]
                hash = md5(filename.encode() + str(datetime.datetime.now()).encode()).hexdigest()
                file = open(f'media/picture/{hash[:6]}.jpg', 'wb')
                file.write(result.content)
                file.close()
            image = Image.open(file.name)
            picture = ImageModel.objects.create(
                picture=file.name,
                name=hash[:6] + '.jpg',
                url=request.data['url'],
                width=image.size[0],
                height=image.size[1],
            )
        image_data = self.serializer_class(picture).data
        return Response(image_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def resize(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.url:
            size = (int(request.data['width']), int(request.data['height']))
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
            return Response(self.serializer_class(new_instance).data, status.HTTP_201_CREATED)
        else:
            size = (int(request.data['width']), int(request.data['height']))
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