from rest_framework import serializers as s

from .models import QRCode


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
