from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Image


class TestImageView(APITestCase):

    def setUp(self) -> None:
        Image.objects.create(
            picture='testfile.jpg',
            name='test',
            width=200,
            height=200,
        )

    def test_get_all_images(self):
        url = 'http://127.0.0.1:8000/api/images/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_detail_images(self):
        instance = Image.objects.get(name='test')
        url = f'http://127.0.0.1:8000/api/images/{instance.id}/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'id': 1,
            'picture': 'http://testserver/media/testfile.jpg',
            'name': 'test',
            'url': None,
            'width':200,
            'height':200,
            'parent_picture': None,
        })

    def test_post_images_url(self):
        url = 'http://127.0.0.1:8000/api/images/'
        response = self.client.post(url, format='json', data={
            'url': 'https://bipbap.ru/wp-content/uploads/2017/05/1_541c78083f3f8541c78083f438-730x548.jpg',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_images_file(self):
        url = 'http://127.0.0.1:8000/api/images/'
        response = self.client.post(url, format='json', data={
            'file': 'file2.jpg',
        })
        self.assertEqual(response.status_code, 200)

    def test_resize(self):
        instance = Image.objects.get(name='test')
        url = f'http://127.0.0.1:8000/api/images/{instance.id}/resize/'
        responce = self.client.post(url, format='json', data={'width': 300, 'heigth': 300})
        self.assertEqual(responce.status_code, 200)
