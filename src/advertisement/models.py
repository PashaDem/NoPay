from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Balance(models.Model):
    total = models.PositiveIntegerField(default=0, verbose_name="Текущий баланс")
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Владелец баланса"
    )


class Payout(models.Model):
    ACCURAL = "accural"
    OFF = "off"

    OP_TYPES = {
        ACCURAL: "accural",
        OFF: "off",
    }

    operation_type = models.CharField(
        max_length=20, verbose_name="Тип операции", choices=OP_TYPES
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время выплаты")
    payout_sum = models.PositiveSmallIntegerField(
        default=1, verbose_name="Сумма выплаты"
    )

    balance = models.ForeignKey(
        Balance, on_delete=models.CASCADE, verbose_name="Баланс"
    )
