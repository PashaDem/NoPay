from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from advertisement.models import Balance, Payout

User = get_user_model()


class PaymentService:
    @atomic
    def process_advertisement_view(self, user: User) -> None:
        """
        Пополняем баланс пользователя
        """
        user_balance, _ = Balance.objects.get_or_create(user=user)
        payout = Payout.objects.create(
            balance=user_balance,
            operation_type=Payout.ACCURAL,
        )
        user_balance.total += payout.payout_sum
        user_balance.save()

    @atomic
    def process_qrcode_uploading(self, user: User) -> None:
        user_balance, _ = Balance.objects.get_or_create(user=user)
        payout = Payout.objects.create(
            balance=user_balance,
            operation_type=Payout.ACCURAL,
            payout_sum=settings.TOKENS_PAYOUT_COUNT_ON_UPLOADING,
        )
        user_balance.total += payout.payout_sum
        user_balance.save()
