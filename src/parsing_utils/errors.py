from common.docstring_exc import DocStringException


class BaseParsingError(DocStringException):
    """Что-то не так с разпознаванием данных токена."""


class InvalidTokenError(BaseParsingError):
    """Не умеем парсить такое =("""


class NoRegistrationSignError(BaseParsingError):
    """Не нашли регистрационного знака на картинке =("""
