from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from qrcode_app.models import QRCode, QRCodeProcessingStatus


@admin.register(QRCode)
class QRCodeAdmin(ModelAdmin):
    ...


@admin.register(QRCodeProcessingStatus)
class QRCodeProcessingStatusAdmin(ModelAdmin):
    ...
