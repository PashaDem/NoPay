import binascii
from base64 import b64decode
from datetime import datetime
from logging import getLogger
from typing import TypedDict

from .errors import InvalidTokenError

logger = getLogger(__name__)


class TokenData(TypedDict):
    transport_id: str
    payment_date: datetime.date
    payment_time: datetime.time
    ticket_id: str
    qr_token: str


def parse_qrcode_content(content: str) -> TokenData:
    try:
        decoded_content = b64decode(content).decode()
    except binascii.Error as err:
        logger.error(f"Не получается декодировать текст QR кода: {err}")
        raise InvalidTokenError

    parts = decoded_content.split(";")
    try:
        transport_id = parts[-2]
        date_and_time = parts[-3]
        ticket_id = parts[-4]
        ticket_prefix = parts[-5]
    except IndexError:
        logger.error(
            "Не можем обработать токен. Не получилось достать нужные сегменты."
        )
        raise InvalidTokenError

    try:
        datetime_obj = datetime.strptime(date_and_time, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError as err:
        logger.error(f"Ошибка во время парсинга даты: {err}")
        return InvalidTokenError

    payment_time = datetime_obj.time()
    payment_date = datetime_obj.date()

    ticket_id = ticket_prefix + ticket_id

    return {
        "transport_id": transport_id,
        "payment_date": payment_date,
        "payment_time": payment_time,
        "ticket_id": ticket_id,
        "qr_token": decoded_content,
    }
