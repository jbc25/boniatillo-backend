# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta, time
from django.db import models
from django.db.models import Sum, CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver

from currency.models import Person
from wallets.models import Wallet


class Activity(models.Model):

    name = models.CharField(null=True, blank=True, verbose_name='Nombre', max_length=250)
    type_activity = models.CharField(null=True, blank=True, verbose_name='Tipo', max_length=250)
    description = models.TextField(null=True, blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['name']

    def __unicode__(self):
        return self.name if self.name else ''

    def __str__(self):
        return self.__unicode__()


class PersonActivity(models.Model):

    activity = models.ForeignKey(Activity, related_name='user_activity', verbose_name='Actividad', on_delete=CASCADE)
    person = models.ForeignKey(Person, null=True, related_name='activities', verbose_name='Persona que realiza la actividad', on_delete=CASCADE)
    day = models.DateField(verbose_name='Día de tarea', default=datetime.now)
    daytime = models.TimeField(verbose_name='Hora de la tarea', default=datetime.now)
    time_spent = models.TimeField(default=0, verbose_name='Tiempo empleado')

    class Meta:
        verbose_name = 'Actividad realizada'
        verbose_name_plural = 'Actividades realizadas'
        ordering = ['day']

    def __unicode__(self):
        display = ''
        if self.person:
            display += self.person.full_name.strip() + ' - '
        if self.activity:
            display += self.activity.name if self.activity.name else ''

        return display

    def __str__(self):
        return self.__unicode__()


CURRENCY_PER_HOUR = 5.00

# Method to pay activity to user
@receiver(post_save, sender=PersonActivity)
def pay_activity(sender, instance, created, **kwargs):

    if created:
        user_wallet = instance.person.user.wallet

        time_amount = instance.time_spent.hour * 60 + instance.time_spent.minute

        '''
        start_day = instance.day - timedelta(days=instance.day.weekday())

        work_done = PersonActivity.objects.filter(person=instance.person, day__gte=start_day)
        # Since aggregating times doesnt work, traverse all times:
        total_time = 0
        for work in work_done:
            total_time += work.time_spent.hour * 60 + work.time_spent.minute

        previous_time = total_time - time_amount
        if total_time < 60:
            # not enough yet
            return
        elif previous_time < 60:
            time_amount = total_time - 60
        '''

        amount = time_amount * CURRENCY_PER_HOUR / 60
        amount = float("%.2f" % amount)  # Truncate to 2 decimals

        Wallet.debit_transaction(user_wallet, amount, concept='Actividad: ' + instance.activity.name)
