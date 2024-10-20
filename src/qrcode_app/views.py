from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from image_service import FileService, MinioFileRepository, UploadFileError
from qrcode_app.serializers import UploadQRCodeSerializer


class UploadQRCodeAPIView(APIView):
    serializer = UploadQRCodeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        This endpoint accepts a QR code image and
        returns ticket_id, transport_id, payment_date, payment_time, registration_sign, qr_token.
        The QR code image is expected to be in request.FILES['image'].
        """
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = request.FILES["image"]

        file_ext = file_obj.name.split(".")[-1]
        try:
            file_service = FileService(MinioFileRepository())
            file_service.process_qr_code(file_obj, request.user.id, file_ext)
        except UploadFileError as err:
            return Response(
                {"message": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"message": "Файл был успешно загружен"})
