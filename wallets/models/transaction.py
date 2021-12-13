# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.db.models import CASCADE

from wallets.models import Wallet



class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_from = models.ForeignKey(Wallet, blank=True, null=True, related_name='transactions_from', on_delete=CASCADE)
    wallet_to = models.ForeignKey(Wallet, related_name='transactions_to', on_delete=CASCADE)
    amount = models.FloatField(default=0, verbose_name='Cantidad')
    concept = models.TextField(blank=True, null=True, verbose_name='Concepto')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')

    tax_processed = models.BooleanField(default=False, verbose_name='Impuestos procesados')
    made_byadmin = models.BooleanField(default=False, verbose_name='Realizada por admin')
    is_bonification = models.BooleanField(default=False, verbose_name='Bonificación')
    is_euro_purchase = models.BooleanField(default=False, verbose_name='Compra de euros')

    rel_transaction = models.ForeignKey('self', null=True, blank=True, on_delete=CASCADE)
    comments = models.TextField(null=True, blank=True, verbose_name='Comentarios adicionales')

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['timestamp']

    def __str__(self):
        return "%s -> %.2f" % (self.concept, round(self.amount, 2))
