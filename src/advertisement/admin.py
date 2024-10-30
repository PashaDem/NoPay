from django.contrib import admin

from .models import Balance, Payout


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    ...


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    ...
