from rest_framework import serializers as s


class UploadQRCodeSerializer(s.Serializer):
    image = s.ImageField()
