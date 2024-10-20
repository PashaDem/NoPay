from django.urls import path

from .views import QrCodeListView, UploadQRCodeAPIView

urlpatterns = [
    path("upload_qr_code/", UploadQRCodeAPIView.as_view(), name="upload_qr_code"),
    path("qr_codes/", QrCodeListView.as_view(), name="qr_codes"),
]
