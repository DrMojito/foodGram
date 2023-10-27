from colorfield.fields import ColorField
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = ColorField(format='hex', default='#778899', unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
