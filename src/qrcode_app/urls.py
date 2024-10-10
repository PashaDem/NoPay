from django.urls import path

from .views import UploadQRCodeAPIView

urlpatterns = [
    path("upload_qr_code/", UploadQRCodeAPIView.as_view(), name="upload_qr_code"),
]
