from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('images', viewset=views.ImageViewSet, basename='images')
# router.register('im', viewset=views.Im, basename='im')


urlpatterns = [
    path('', include(router.urls)),
]