# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth import hashers
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum, CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver

from currency.models import Entity, Person
from helpers import notify_user
from wallets.exceptions import NotEnoughBalance, WrongPinCode
from wallets.models import WalletType


class Wallet(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, null=True, on_delete=CASCADE)
    type = models.ForeignKey(WalletType, null=True, related_name='wallets', on_delete=CASCADE)
    balance = models.FloatField(default=0, verbose_name='Saldo actual')
    last_transaction = models.DateTimeField(blank=True, null=True, verbose_name='Última transacción')
    pin_code = models.CharField(null=True, blank=True, max_length=100, verbose_name='Código PIN (hasheado)')

    NotEnoughBalance = NotEnoughBalance
    WrongPinCode = WrongPinCode

    class Meta:
        verbose_name = 'Monedero'
        verbose_name_plural = 'Monederos'
        ordering = ['user']

    def __unicode__(self):
        if self.user:
            return self.user.username + ': ' + str(self.balance)
        elif self.type:
            return self.type.id + ': ' + str(self.balance)
        else:
            return 'Unknown wallet'

    def __str__(self):
        return self.__unicode__()

    def set_type(self, type='default'):
        if not type:
            type = 'default'
        try:
            wallet_type = WalletType.objects.get(id=type)
        except WalletType.DoesNotExist:
            wallet_type = None

        if wallet_type:
            self.type = wallet_type
            self.save()

    @property
    def credit_balance(self):
        from wallets.models import Payment
        pending_payments = Payment.objects.pending().filter(sender=self.user).aggregate(sum=Sum('currency_amount'))
        pending_amount = 0 if not pending_payments['sum'] else pending_payments['sum']

        credit_limit = 0.0 if not self.type else self.type.credit_limit
        balance = self.balance + credit_limit - pending_amount

        return balance

    def has_enough_balance(self, amount_to_pay, payment=None):
        from wallets.models.payment import STATUS_PENDING
        if self.type and self.type.unlimited:
                return True

        credit_balance = self.credit_balance
        # we dont add the current payment to the credit balance
        if payment and payment.status == STATUS_PENDING:
            credit_balance += payment.currency_amount

        return amount_to_pay <= credit_balance

    @transaction.atomic
    def new_transaction(self, amount, wallet=None, concept=None, bonus=False, is_euro_purchase=False, from_payment=None, made_byadmin=False, **kwargs):

        if wallet:
            wallet_from = self
            wallet_to = wallet
        else:
            wallet_from = None
            wallet_to = self

        if not concept:
            if bonus:
                concept = "Bonificación en boniatos por compra"
            elif wallet_from:
                concept = "Transferencia"

        if wallet_from and not wallet_from.has_enough_balance(amount, payment=from_payment):
            raise NotEnoughBalance

        from wallets.models.transaction import Transaction
        transaction = Transaction.objects.create(
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            amount=amount,
            is_bonification=bonus,
            concept=concept,
            made_byadmin=made_byadmin,
            is_euro_purchase=is_euro_purchase,
            **kwargs)

        if wallet_from:
            wallet_from.update_balance(transaction, is_sender=True)
        wallet_to.update_balance(transaction, is_receiver=True)

        return transaction


    @transaction.atomic
    def update_balance(self, new_transaction, is_sender=False, is_receiver=False):
        self.last_transaction = new_transaction.timestamp

        if is_sender:
            self.balance -= new_transaction.amount
        if is_receiver:
            self.balance += new_transaction.amount

        from wallets.models import TransactionLog
        TransactionLog.objects.create_log(self, new_transaction, self.balance)

        self.save()


    def notify_transaction(self, transaction, silent=False):
        data = {
            'type': 'transaction',
            'amount': transaction.amount,
            'is_bonification': transaction.is_bonification,
            'is_euro_purchase': transaction.is_euro_purchase,
            'concept': transaction.concept
        }

        title = 'Ya tienes tu bonificación!' if transaction.is_bonification else 'Has recibido una transferencia'
        notify_user(self.user, title=title, message=data['concept'], data=data, silent=silent)


    def update_pin_code(self, pin_code):
        self.pin_code = hashers.make_password(pin_code)
        self.save()

    @staticmethod
    def update_user_pin_code(user, pin_code):
        wallet = Wallet.objects.filter(user=user).first()
        if wallet:
            wallet.update_pin_code(pin_code)

    @staticmethod
    def debit_transaction(wallet, amount, concept='Compra de boniatos'):
        debit_wallet = Wallet.objects.filter(type__id='debit').first()
        t = debit_wallet.new_transaction(amount, wallet=wallet, concept=concept, is_euro_purchase=True)
        wallet.notify_transaction(t)
        return t

# Method to create the wallet for every new user
@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        print('Creating user wallet!')
        wallet, new = Wallet.objects.get_or_create(user=instance)

        type, related = instance.get_related_entity()
        wallet_type = 'entity' if type == 'entity' else 'default'
        wallet.set_type(wallet_type)

        if not new:
            print('Wallet for user already existed')


# Method to generate the entity wallet type
@receiver(post_save, sender=Entity)
def add_user_to_group(sender, instance, created, **kwargs):

    if created:
        wallet, new = Wallet.objects.get_or_create(user=instance.user)
        wallet.set_type('entity')

# Method to generate the person wallet type
@receiver(post_save, sender=Person)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        wallet, new = Wallet.objects.get_or_create(user=instance.user)
        wallet.set_type('default')
