from rest_framework import serializers as s

from .models import QRCode


class UploadQRCodeSerializer(s.Serializer):
    image = s.ImageField()


class PublicTicketSerializer(s.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ("id", "registration_sign", "transport_id")
