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
    users = models.ManyToManyField(
        User, related_name="qrcodes", verbose_name="Пользователи"
    )


class QRCodeProcessingStatus(models.Model):
    """
    Отслеживаем статус для того, чтобы сообщать пользователям,
    о возникновении ошибки / об успешной обработке qr-кода.
    """

    ERROR = "error"
    SUCCESS = "success"
    STATUSES = {
        ERROR: ERROR,
        SUCCESS: SUCCESS,
    }

    status = models.CharField(choices=STATUSES, max_length=20)
    # поле для подробного описания возникшей ошибки
    description = models.CharField(max_length=100, null=True, blank=True)
    # для того, чтобы находить для пользователя самую актуальную инфу о статусах
    # и чистить старые статусы на основании этой информации
    created_at = models.DateTimeField(auto_now=True)
    qrcode = models.OneToOneField(
        QRCode, on_delete=models.SET_NULL, null=True, blank=True
    )
    # быстрый поиск уведомлений для пользователя
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    was_seen_by_user = models.BooleanField(
        default=False, verbose_name="Видел ли пользователь это уведомление?"
    )
