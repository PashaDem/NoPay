import os

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model

from parsing_utils.errors import BaseParsingError
from parsing_utils.parse_minsktrans_token import parse_image_text
from parsing_utils.parse_reg_sign import parse_qrcode_content
from qrcode_app.models import QRCode

from .minio_factory import MinioFileRepository

logger = get_task_logger(__name__)

User = get_user_model()


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
        decoded_qrcodes = decode(Image.open(local_filename))
        if len(decoded_qrcodes):
            qrcode_text = decoded_qrcodes[0].data
        else:
            logger.error("QR код не был найден")
            return
    except Exception as err:
        logger.error(f"Ошибка во время парсинга картинки: {err}")

    try:
        qrcode_payload = parse_qrcode_content(qrcode_text)
    except BaseParsingError as err:
        logger.error(err)
        return

    # parse text from ticket image
    registration_sign = parse_image_text(local_filename)

    qrcode_payload.update(
        {
            "registration_sign": registration_sign,
            "created_by": User.objects.get(id=user_id),
        }
    )

    QRCode.objects.create(**qrcode_payload)
    repo.remove_file_from_blob(settings.MINIO_BUCKET_NAME, filename)

    if os.path.exists(local_filename):
        os.remove(local_filename)