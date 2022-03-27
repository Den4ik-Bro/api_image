from django.db import models
from django.db.models import PROTECT


class Image(models.Model):
    picture = models.ImageField(verbose_name='картинка', upload_to='picture')
    name = models.CharField(max_length=100, verbose_name='название')
    url = models.CharField(max_length=200, verbose_name='ссылка', null=True, blank=True)
    width = models.PositiveSmallIntegerField(verbose_name='ширина')
    height = models.PositiveSmallIntegerField(verbose_name='высота')
    parent_picture = models.ForeignKey('self', on_delete=PROTECT, null=True, blank=True, related_name='descendants')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'

    def __str__(self):
        return self.name