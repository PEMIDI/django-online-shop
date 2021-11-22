from django.contrib import admin

from transaction.models import Transaction, TransactionArchive, UserBalance


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'create_time')


@admin.register(TransactionArchive)
class TransactionArchiveAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'create_time')


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'create_time')
