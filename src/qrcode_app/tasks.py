from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.transaction import atomic
from django.utils import timezone


@shared_task
@atomic
def clear_not_relevant_qrcodes():
    from .models import QRCode

    logger = get_task_logger(__name__)

    current_datetime = timezone.now()
    # Сегодняшние неактуальные qr коды
    QRCode.objects.filter(
        payment_date=current_datetime.date(),
        payment_time__lte=(current_datetime - timedelta(hours=2)).time(),
    ).delete()
    # Неактуальные коды, оставшиеся за предыдущие дни
    QRCode.objects.filter(payment_date__lt=current_datetime.date()).delete()

    logger.info("Successfully remove not relevant qrcodes.")
