from common.docstring_exc import DocStringException


class BaseQRCodeServiceError(DocStringException):
    """Общая ошибка для сервиса QR-кодов."""


class QRCodeNotFound(BaseQRCodeServiceError):
    """QR-код не был найден."""


class NotEnoughTokens(BaseQRCodeServiceError):
    """Недостаточно токенов для покупки QR-кода."""


class QRCodeAlreadyPurchased(BaseQRCodeServiceError):
    """QR-код уже был куплен."""
