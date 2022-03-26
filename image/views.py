import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from .models import Image as ImageModel
from .serializers import ImageSerializer, UploadImageSerializer, UpdateImageSerializer
from PIL import Image
import requests
from hashlib import md5


class ImageViewSet(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = ImageModel.objects.all()

    # def create(self, request, *args, **kwargs):
    #     if request.data.get('file') != None:
    #         file = request.data['file']
    #         image = Image.open(file)
    #         picture = ImageModel.objects.create(
    #             picture=file,
    #             name=file.name,
    #             width=image.size[0],
    #             height=image.size[1],
    #         )
    #     else:
    #         result = requests.get(url=request.data['url'], stream=True)
    #         if result.status_code == 200:
    #             filename = request.data['url'].split('/')[-1]
    #             hash = md5(filename.encode() + str(datetime.datetime.now()).encode()).hexdigest()
    #             file = open(f'media/picture/{hash[:6]}.jpg', 'wb')
    #             file.write(result.content)
    #             file.close()
    #         image = Image.open(file.name)
    #         picture = ImageModel.objects.create(
    #             picture=file.name,
    #             name=hash[:6] + '.jpg',
    #             url=request.data['url'],
    #             width=image.size[0],
    #             height=image.size[1],
    #         )
    #     image_data = self.serializer_class(picture).data
    #     return Response(image_data, status=status.HTTP_201_CREATED)

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
                image_data = self.serializer_class(picture).data
                return Response(image_data)
            else:
                url = serializer.validated_data['url']
                result = requests.get(url=url, stream=True)
                if result.status_code == 200:
                    filename = url.split('/')[-1]
                    hash = md5(filename.encode() + str(datetime.datetime.now()).encode()).hexdigest()
                    file = open(f'media/picture/{hash}.jpg', 'wb')
                    file.write(result.content)
                    file.close()
                    # print(file.name)
                    # filename = file.name
                image = Image.open(file.name)
                picture = ImageModel.objects.create(
                    picture=f'media/picture/{hash}.jpg',
                    name=hash,
                    url=url,
                    width=image.size[0],
                    height=image.size[1],
                )
                image_data = self.serializer_class(picture).data
                return Response(image_data)
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
                return Response(self.serializer_class(new_instance).data, status.HTTP_201_CREATED)
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

# class Im(ViewSet):
#
#     def list(self, request):
#         queryset = ImageModel.objects.all()
#         serializer = ImageSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, pk=None):
#         queryset = ImageModel.objects.all()
#         instance = get_object_or_404(queryset, pk=pk)
#         serializer = ImageSerializer(instance)
#         return Response(serializer.data)
#
#     def create(self, request, *args, **kwargs):
#         serializer = UploadImageSerializer(data=request.data)
#         if serializer.is_valid():
#             if 'file' in serializer.validated_data and serializer.validated_data['file']:
#                 file = serializer.validated_data['file']
#                 filename = file
#             else:
#                 url = serializer.validated_data['url']
#                 result = requests.get(url=url, stream=True)
#                 if result.status_code == 200:
#                     filename = url.split('/')[-1]
#                     file = open(f'media/picture/{filename}', 'wb')
#                     file.write(result.content)
#                     file.close()
#                     filename = file.name
#         image = Image.open(filename)
#         picture = ImageModel.objects.create(
#             picture=filename,
#             width=image.size[0],
#             height=image.size[1],
#         )
#         image_data = self.serializer_class(picture).data
#         return Response(image_data)