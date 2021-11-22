from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import Coalesce


class Transaction(models.Model):
    CHARGE = 1
    TRANSFER_RECEIVED = 3

    PURCHASE = 2
    TRANSFER_SENT = 4

    TRANSACTION_TYPE_CHOICES = (
        (CHARGE, 'Charge'),
        (PURCHASE, 'Purchase'),
        (TRANSFER_RECEIVED, 'Transfer Received'),
        (TRANSFER_SENT, 'Transfer Sent'),
    )

    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    transaction_type = models.SmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES,
        default=CHARGE
    )
    amount = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.get_transaction_type_display()} - {self.amount}'

    @classmethod
    def get_report(cls):
        """Show all users and their balance"""
        positive_transactions = Sum(
            'transactions__amount',
            filter=Q(transactions__transaction_type__in=[1, 3])
        )
        negative_transactions = Sum(
            'transactions__amount',
            filter=Q(transactions__transaction_type__in=[2, 4])
        )

        users = User.objects.annotate(
            transaction_count=Count('transactions__id'),
            balance_=Coalesce(positive_transactions, Value(0)) - Coalesce(negative_transactions, Value(0))
        )
        return users

    @classmethod
    def get_total_balance(cls):
        """Sum balance all users"""
        qs = cls.get_report()
        return qs.aggregate(balance=Sum('get_balance'))

    @classmethod
    def user_balance(cls, user):
        """Calculate balance user"""
        positive_transactions = Sum(
            'amount',
            filter=Q(transaction_type__in=[1, 3])
        )
        negative_transactions = Sum(
            'amount',
            filter=Q(transaction_type__in=[2, 4])
        )

        user_balance = user.transactions.all().aggregate(
            balance=Coalesce(positive_transactions, Value(0)) - Coalesce(negative_transactions, Value(0))
        )
        return user_balance.get('balance', 0)


class TransactionArchive(models.Model):
    CHARGE = 1
    TRANSFER_RECEIVED = 3

    PURCHASE = 2
    TRANSFER_SENT = 4

    TRANSACTION_TYPE_CHOICES = (
        (CHARGE, 'Charge'),
        (PURCHASE, 'Purchase'),
        (TRANSFER_RECEIVED, 'Transfer Received'),
        (TRANSFER_SENT, 'Transfer Sent'),
    )

    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name='transactions_archive'
    )
    transaction_type = models.SmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES,
        default=CHARGE
    )
    amount = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.get_transaction_type_display()} - {self.amount}'


class UserBalance(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.PROTECT,
        related_name='balance'
    )
    balance = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.balance} - {self.create_time}'

    @classmethod
    def record_user_balance(cls, user):
        """Save balance user at time"""
        balance = Transaction.user_balance(user)

        instance = cls.objects.create(user=user, balance=balance)
        return instance

    @classmethod
    def record_all_user_balance(cls):
        """Save balance users at time"""
        users = User.objects.all()
        for user in users:
            record = cls.record_user_balance(user)
            print(record)


class TransferTransaction(models.Model):
    sender_transaction = models.ForeignKey(
        to=Transaction,
        on_delete=models.PROTECT,
        related_name='send_transfers'
    )
    receiver_transaction = models.ForeignKey(
        to=Transaction,
        on_delete=models.PROTECT,
        related_name='received_transfers'
    )
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender_transaction} - {self.receiver_transaction} - {self.create_time}'

    @classmethod
    def transfer(cls, sender, receiver, amount):
        """Transfer amount between two users"""
        if Transaction.user_balance(user=sender) < amount:
            return 'Transaction not allowed, insufficient balance'

        with transaction.atomic():
            sender_transaction = Transaction.objects.create(
                user=sender,
                transaction_type=Transaction.TRANSFER_SENT,
                amount=amount
            )
            receiver_transaction = Transaction.objects.create(
                user=receiver,
                transaction_type=Transaction.TRANSFER_RECEIVED,
                amount=amount
            )

            instance = cls.objects.create(
                sender_transaction=sender_transaction,
                receiver_transaction=receiver_transaction
            )

        return instance


class UserScore(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='user_score'
    )
    score = models.PositiveSmallIntegerField(default=0)

    class Meta:
        permissions = (
            ('has_score_permission', 'Has score permission'),
        )

    @classmethod
    def change_score(cls, user, score):
        qs = cls.objects.select_for_update().filter(user=user)
        with transaction.atomic():
            if qs.exists():
                instance = qs.first()
            else:
                instance = cls.objects.create(user=user, score=0)
            instance.score += score
            instance.save()
