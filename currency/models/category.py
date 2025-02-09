# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models


class Category(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True, verbose_name='Nombre', max_length=250)
    description = models.TextField(null=True, blank=True, verbose_name='Descripción')
    color = models.CharField(null=True, blank=True, verbose_name='Color de etiqueta (código hexadecimal)', max_length=30)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __unicode__(self):
        return self.name if self.name else ''

    def __str__(self):
        return self.__unicode__()