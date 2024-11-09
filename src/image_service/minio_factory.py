from logging import getLogger

from django.conf import settings
from minio import Minio
from minio.error import S3Error

from image_service.errors import DownloadFileError, RemoveFileError, UploadFileError

logger = getLogger(__name__)


class MinioFileRepository:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_HOST,
            access_key=settings.MINIO_DJANGO_USER,
            secret_key=settings.MINIO_DJANGO_PASSWORD,
            secure=False,
        )

    def upload_file_to_blob(
        self, file_obj: bytes, bucket: str, destination_filename: str
    ) -> None:
        try:
            self._confirm_bucket_exists(bucket)
            self.client.put_object(
                bucket, destination_filename, file_obj, len(file_obj)
            )
        except S3Error as err:
            logger.error(err)
            raise UploadFileError from None

    def _confirm_bucket_exists(self, bucket: str) -> None:
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)
        return self.client.bucket_exists(bucket)

    def check_filename_uniqueness(self, filename: str, bucket: str) -> bool:
        """
        :return: False, если файл с таким именем уже существует
        """
        objs = self.client.list_objects(bucket)
        return not any(filename == obj_name for obj_name in objs)

    def download_file_from_blob(self, bucket: str, filename: str) -> str:
        """
        :raises DownloadFileError: не удалось скачать файл из blob-хранилища
        :return: путь к скачанному файлу
        """
        try:
            self.client.fget_object(bucket, filename, settings.DOWNLOAD_DIR + filename)
            return settings.DOWNLOAD_DIR + filename
        except S3Error as err:
            logger.error(err)
            raise DownloadFileError from None

    def remove_file_from_blob(self, bucket: str, filename: str):
        """
        :raises RemoveFileError: не удалось удалить файл из blob-хранилища
        """
        try:
            self.client.remove_object(bucket, filename)
        except S3Error as err:
            logger.error(err)
            raise RemoveFileError from None
