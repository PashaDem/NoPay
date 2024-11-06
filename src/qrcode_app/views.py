from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.order_by_payment_datetime import order_by_payment_datetime
from image_service import FileService, MinioFileRepository, UploadFileError
from qrcode_app.models import QRCode
from qrcode_app.permissions import IsOwnerOrAuthenticated, NotOwnerAndAuthenticated
from qrcode_app.serializers import (
    PublicTicketSerializer,
    QRCodePrivateSerializer,
    QRCodePublicSerializer,
    UploadQRCodeSerializer,
)

from .errors import BaseQRCodeServiceError
from .qrcode_service import QRCodeService


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
    get=extend_schema(
        summary="Список доступных QR-кодов",
        parameters=[
            OpenApiParameter(
                name="is_trolleybus",
                location=OpenApiParameter.QUERY,
                description='Используется для фильтрации вместе с query параметром "transport_number". 1 = true, 0 = false',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="is_train",
                location=OpenApiParameter.QUERY,
                description='Используется для фильтрации вместе с query параметром "transport_number". 1 = true, 0 = false',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="is_bus",
                location=OpenApiParameter.QUERY,
                description='Используется для фильтрации вместе с query параметром "transport_number". 1 = true, 0 = false',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="transport_number",
                location=OpenApiParameter.QUERY,
                description='Публичный номер транспорта - 10, 25, который указывается на автобусе/троллейбусе. Используется только вместе с query параметром "is_trolleybus".',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="reg_sign",
                location=OpenApiParameter.QUERY,
                description="Фильтрует по полному названию регистрационного знака. Это значение находится под qr кодом в самом транспорте.",
                required=False,
                type=str,
            ),
        ],
        responses={status.HTTP_200_OK: PublicTicketSerializer(many=True)},
    )
)
class QrCodeListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PublicTicketSerializer
    queryset = QRCode.objects.all()

    @order_by_payment_datetime
    def get_queryset(self):
        prefixes = {
            "is_trolleybus": "Т",
            "is_train": "Тр",
            "is_bus": "А",
        }
        values = {
            "is_trolleybus": self.request.query_params.get("is_trolleybus"),
            "is_bus": self.request.query_params.get("is_bus"),
            "is_train": self.request.query_params.get("is_train"),
        }

        prefix = None
        for key, val in values.items():
            if val and val.isdigit():
                prefix = prefixes[key]

        # not transport id
        transport_number = self.request.query_params.get("transport_number", "")

        if prefix and transport_number is not None:
            ind = f"{prefix}_№{transport_number}"
            return self.queryset.filter(registration_sign__icontains=ind)

        transport_reg_sign = self.request.query_params.get("reg_sign")
        if transport_reg_sign is not None:
            return self.queryset.filter(registration_sign__icontains=transport_reg_sign)

        return self.queryset.all()


@extend_schema_view(
    get=extend_schema(
        summary="Получение QR кода по ID",
        responses={status.HTTP_200_OK: QRCodePrivateSerializer},
    )
)
class QRCodeDetailView(RetrieveAPIView):
    permission_classes = (IsOwnerOrAuthenticated,)
    queryset = QRCode.objects.all()

    def get_serializer_class(self):
        code = self.get_object()
        user = self.request.user

        if (
            user == code.created_by
            or code.users.filter(id=user.id).exists()
            or user.is_superuser
        ):
            return QRCodePrivateSerializer
        else:
            return QRCodePublicSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Осуществление покупки qr-кода за токены",
        responses={
            status.HTTP_200_OK: None,
            status.HTTP_400_BAD_REQUEST: inline_serializer(
                name="Сообщение об ошибке при покупке QR-кода",
                fields={
                    "message": serializers.CharField(),
                },
            ),
        },
    )
)
class BuyQRCodeAPIView(APIView):
    permission_classes = (NotOwnerAndAuthenticated,)

    def post(self, request, pk):
        service = QRCodeService()
        try:
            service.buy_qrcode(user=request.user, qrcode_id=pk)
        except BaseQRCodeServiceError as err:
            return Response({"message": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        summary="Получение QR-кодов, созданных или купленных пользователем",
        responses={status.HTTP_200_OK: QRCodePrivateSerializer},
    )
)
class UserQRCodesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        qs = QRCode.objects.filter(Q(users__in=[user]) | Q(created_by=user))
        return Response(QRCodePrivateSerializer(qs, many=True).data)
