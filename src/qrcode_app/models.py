from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class QRCode(models.Model):
    ticket_id = models.CharField(
        max_length=15, unique=True, verbose_name="Номер билета"
    )
    transport_id = models.CharField(max_length=20, verbose_name="Номер ТС")
    payment_date = models.DateField(verbose_name="Дата покупки")
    payment_time = models.TimeField(verbose_name="Время")
    registration_sign = models.CharField(verbose_name="Рег. Знак")
    qr_token = models.TextField(verbose_name="Токен из QR-кода")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь, выгрузивший токен"
    )
