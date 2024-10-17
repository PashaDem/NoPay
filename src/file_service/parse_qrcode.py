from base64 import b64decode
from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from qrcode_app.models import QRCode

from .minio_factory import MinioFileRepository

logger = get_task_logger(__name__)


def parse_qrcode(filename: str, user_id: int):
    parse_qrcode_task.delay(filename, user_id)


@shared_task
def parse_qrcode_task(filename: str, user_id: int) -> None:
    from PIL import Image
    from pyzbar.pyzbar import decode

    repo = MinioFileRepository()
    try:

        local_filename = repo.download_file_from_blob(
            settings.MINIO_BUCKET_NAME, filename
        )
    except Exception as err:
        logger.error(f"Ошибка скачивания файла : {err} | filename: {filename}")
        return

    try:
        qrcode_text = decode(Image.open(local_filename))[0].data
    except Exception as err:
        logger.error(f"Ошибка во время парсинга картинки: {err}")

    try:
        qrcode_payload = parse_qrcode_content(qrcode_text)
    except Exception as err:
        logger.error(err)
        return

    QRCode.objects.create(**qrcode_payload, created_by=user_id)
    repo.remove_file_from_blob(settings.MINIO_BUCKET_NAME, filename)


def parse_qrcode_content(content: str) -> dict:
    decoded_content = b64decode(content).decode()

    parts = decoded_content.split(";")
    transport_id = parts[-2]
    date_and_time = parts[-3]

    try:
        datetime_obj = datetime.strptime(date_and_time, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError as err:
        logger.error(f"Ошибка во время парсинга даты: {err}")
        return {}

    payment_time = datetime_obj.time()
    payment_date = datetime_obj.date()

    ticket_id = parts[-4]
    ticket_prefix = parts[-5]

    ticket_id = ticket_prefix + ticket_id

    return {
        "transport_id": transport_id,
        "payment_date": payment_date,
        "payment_time": payment_time,
        "ticket_id": ticket_id,
        "qr_token": decoded_content,
        "registration_sign": "",
    }
