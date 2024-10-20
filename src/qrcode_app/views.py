from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from image_service import FileService, MinioFileRepository, UploadFileError
from qrcode_app.models import QRCode
from qrcode_app.serializers import PublicTicketSerializer, UploadQRCodeSerializer


class UploadQRCodeAPIView(APIView):
    serializer = UploadQRCodeSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Подгрузка QR кода.",
        tags=["qrcode"],
        request={
            "multipart/form-data": UploadQRCodeSerializer,
        },
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="Сообщение об успешной загрузке QR кода",
                fields={
                    "message": serializers.CharField(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: inline_serializer(
                name="Сообщение об ошибке загрузки QR кода",
                fields={
                    "message": serializers.CharField(
                        default="Файл был успешно загружен"
                    ),
                },
            ),
        },
    )
    def post(self, request):
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


@extend_schema_view(
    list=extend_schema(
        summary="Список доступных QR-кодов",
        tags=["QRCODE"],
        responses={status.HTTP_200_OK: PublicTicketSerializer(many=True)},
    )
)
class QrCodeListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PublicTicketSerializer
    queryset = QRCode.objects.all()

    def get_queryset(self):

        is_trolleybus = self.request.query_params.get("is_trolleybus")
        # not transport id
        transport_number = self.request.query_params.get("transport_number")
        if is_trolleybus and transport_number:
            transport_prefix = "Т" if is_trolleybus else "A"
            ind = f"{transport_prefix}_№{transport_number}"
            return self.queryset.filter(registration_sign__icontains=ind)

        transport_reg_sign = self.request.query_params.get("reg_sign")
        if transport_reg_sign is not None:
            return self.queryset.filter(registration_sign__icontains=transport_reg_sign)

        return self.queryset
