# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-05 13:16
from __future__ import unicode_literals

import helpers
from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('currency', '0012_auto_20180105_1316'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=250, null=True, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripci\xf3n')),
                ('banner_image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=helpers.RandomFileName('offers/'), verbose_name='Imagen principal')),
                ('published_date', models.DateTimeField(auto_now_add=True)),
                ('discount_percent', models.FloatField(blank=True, default=0, null=True, verbose_name='Porcentaje de descuento')),
                ('discounted_price', models.FloatField(blank=True, default=0, null=True, verbose_name='Precio con descuento')),
                ('active', models.BooleanField(verbose_name='Activa')),
                ('begin_date', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha de fin')),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='currency.Entity')),
            ],
            options={
                'ordering': ['-published_date'],
                'verbose_name': 'Oferta',
                'verbose_name_plural': 'Ofertas',
            },
        ),
    ]
