import os
from datetime import datetime, timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model

from feature_toggles.models import FeatureToggles
from image_service.minio_factory import MinioFileRepository
from parsing_utils.errors import BaseParsingError
from parsing_utils.parse_minsktrans_token import parse_image_text
from parsing_utils.parse_reg_sign import parse_qrcode_content
from qrcode_app.models import QRCode

logger = get_task_logger(__name__)

User = get_user_model()


def parse_qrcode(filename: str, user_id: int) -> None:
    parse_qrcode_task.delay(filename, user_id)


@shared_task
def parse_qrcode_task(filename: str, user_id: int) -> None:
    from PIL import Image
    from pyzbar.pyzbar import decode

    from qrcode_app.models import QRCodeProcessingStatus

    user = User.objects.get(id=user_id)

    repo = MinioFileRepository()
    try:
        local_filename = repo.download_file_from_blob(
            settings.MINIO_BUCKET_NAME, filename
        )
    except Exception as err:
        logger.error(f"Ошибка скачивания файла : {err} | filename: {filename}")
        QRCodeProcessingStatus.objects.create(
            created_by=user,
            status=QRCodeProcessingStatus.ERROR,
            description="Невозможно обработать файл из-за внутренней ошибки системы",
        )
        return

    try:
        decoded_qrcodes = decode(Image.open(local_filename))
        if len(decoded_qrcodes):
            qrcode_text = decoded_qrcodes[0].data
        else:
            QRCodeProcessingStatus.objects.create(
                created_by=user,
                status=QRCodeProcessingStatus.ERROR,
                description="Система не может распознать QR-код в данном файле.",
            )
            logger.error("QR код не был найден")
            return
    except Exception as err:
        QRCodeProcessingStatus.objects.create(
            created_by=user,
            status=QRCodeProcessingStatus.ERROR,
            description="Система не может распознать QR-код в данном файле.",
        )
        logger.error(f"Ошибка во время парсинга картинки: {err}")
        return

    try:
        qrcode_payload = parse_qrcode_content(qrcode_text)
    except BaseParsingError as err:
        QRCodeProcessingStatus.objects.create(
            created_by=user,
            status=QRCodeProcessingStatus.ERROR,
            description="Неверный формат QR-кода.",
        )
        logger.error(err)
        return

    date = qrcode_payload["payment_date"]
    time = qrcode_payload["payment_time"]
    datetime_obj = datetime.combine(date, time)

    if (
        FeatureToggles.restrict_old_qrcodes
        and datetime_obj
        < datetime.now() - timedelta(hours=settings.QRCODE_EXPIRATION_HOURS)
    ):
        QRCodeProcessingStatus.objects.create(
            created_by=user,
            status=QRCodeProcessingStatus.ERROR,
            description="Срок действия QR-кода истек.",
        )
        logger.error("Неактуальный QR-код")
        return

    # parse text from ticket image
    try:
        registration_sign = parse_image_text(local_filename)
    except BaseParsingError as err:
        QRCodeProcessingStatus.objects.create(
            created_by=user,
            status=QRCodeProcessingStatus.ERROR,
            description="Система не может распознать регистрационный знак в данном файле.",
        )
        logger.error(err)
        return

    qrcode_payload.update(
        {
            "registration_sign": registration_sign,
            "created_by": user,
        }
    )

    ticket_id = qrcode_payload["ticket_id"]
    if QRCode.objects.filter(ticket_id=ticket_id).exists():
        QRCodeProcessingStatus.objects.create(
            created_by=user,
            status=QRCodeProcessingStatus.ERROR,
            description="Данный QR-код уже был внесен в систему.",
        )
        logger.error("Данный QR-код уже был подгружен")
        return

    QRCode.objects.create(**qrcode_payload)
    repo.remove_file_from_blob(settings.MINIO_BUCKET_NAME, filename)

    if os.path.exists(local_filename):
        os.remove(local_filename)
