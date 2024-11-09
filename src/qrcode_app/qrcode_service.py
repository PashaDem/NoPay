from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from advertisement.models import Balance, Payout
from qrcode_app.errors import NotEnoughTokens, QRCodeAlreadyPurchased, QRCodeNotFound
from qrcode_app.models import QRCode

User = get_user_model()


class QRCodeService:
    @atomic
    def buy_qrcode(self, user: User, qrcode_id: int) -> None:
        qrcode = QRCode.objects.filter(id=qrcode_id).first()
        if not qrcode:
            raise QRCodeNotFound

        balance, created = Balance.objects.get_or_create(user=user)
        if created or balance.total < 1:
            raise NotEnoughTokens

        if user not in qrcode.users.all():
            # даем доступ пользователю
            qrcode.users.add(user)
            Payout.objects.create(
                balance=balance, operation_type=Payout.OFF, payout_sum=1
            )
            balance.total -= 1
            balance.save()
        else:
            raise QRCodeAlreadyPurchased
