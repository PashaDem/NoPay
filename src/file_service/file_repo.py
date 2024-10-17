from typing import Protocol


class IFileRepository(Protocol):
    def upload_file_to_blob(
        self, file_obj: bytes, bucket: str, destination_filename: str
    ):
        """
        :raises UploadFileError: не удалось загрузить файл в blob-хранилище
        """
        ...

    def check_filename_uniqueness(self, filename: str) -> bool:
        """
        :return: False, если файл с таким именем уже существует
        """
        ...

    def download_file_from_blob(self, bucket: str, filename: str) -> str:
        """
        :raises DownloadFileError: не удалось скачать файл из blob-хранилища
        """
        ...

    def remove_file_from_blob(self, bucket: str, filename: str) -> None:
        """
        :raises RemoveFileError: не удалось удалить файл из blob-хранилища
        """
        ...
