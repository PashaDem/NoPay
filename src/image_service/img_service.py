from typing import Literal
from uuid import uuid1

from django.conf import settings

from .file_repo import IFileRepository
from .parse_qrcode import parse_qrcode


class FileService:
    def __init__(self, file_repo: IFileRepository):
        self.repo = file_repo

    def _generate_filename(self, file_ext: Literal["png", "jpg", "jpeg"]) -> str:
        return str(uuid1()) + "." + file_ext

    def process_qr_code(
        self, file_obj: bytes, user_id: int, file_ext: Literal["png", "jpg", "jpeg"]
    ) -> None:
        dest_filename = self._generate_filename(file_ext)
        while not self.repo.check_filename_uniqueness(
            dest_filename, settings.MINIO_BUCKET_NAME
        ):
            dest_filename = self._generate_filename(file_ext)

        self.repo.upload_file_to_blob(
            file_obj, settings.MINIO_BUCKET_NAME, dest_filename
        )

        parse_qrcode(dest_filename, user_id)
