from rest_framework import serializers as s

from qrcode_app.models import QRCode, QRCodeProcessingStatus


class UploadQRCodeSerializer(s.Serializer):
    image = s.ImageField()


class PublicTicketSerializer(s.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ("id", "registration_sign", "transport_id")


class QRCodePrivateSerializer(s.ModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "id",
            "ticket_id",
            "transport_id",
            "payment_date",
            "payment_time",
            "registration_sign",
            "qr_token",
        )


class QRCodePublicSerializer(s.ModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "id",
            "transport_id",
            "registration_sign",
            "ticket_id",
            "payment_date",
            "payment_time",
        )


class QRCodeProcessingStatusSerializer(s.ModelSerializer):
    class Meta:
        """
        Поле qrcode, чтобы на клиенте можно было бы сделать редирект
        на конкретный qr-код.
        id передаем, чтобы клиент мог сообщить о просмотре нотификашки.
        """

        model = QRCodeProcessingStatus
        fields = (
            "id",
            "created_by",
            "status",
            "description",
            "created_at",
            "qrcode",
        )
