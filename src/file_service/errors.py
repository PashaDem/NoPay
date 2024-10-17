from common import DocStringException


class UploadFileError(DocStringException):
    """Невозможно загрузить файл в blob-хранилище"""


class DownloadFileError(DocStringException):
    """Невозможно скачать файл из blob-хранилища"""


class RemoveFileError(DocStringException):
    """Невозможно удалить файл из blob-хранилища"""
