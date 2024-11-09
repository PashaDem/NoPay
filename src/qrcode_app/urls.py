from django.urls import path

from qrcode_app.views import (
    BuyQRCodeAPIView,
    QRCodeDetailView,
    QrCodeListView,
    UploadQRCodeAPIView,
    UserQRCodesAPIView,
)

urlpatterns = [
    path("upload_qr_code/", UploadQRCodeAPIView.as_view(), name="upload_qr_code"),
    path("qr_codes/", QrCodeListView.as_view(), name="qr_codes_list"),
    path("qr_codes/<int:pk>/", QRCodeDetailView.as_view(), name="qr_code_detail"),
    path("qr_codes/<int:pk>/buy", BuyQRCodeAPIView.as_view(), name="buy_qr_code"),
    path("qr_codes/my", UserQRCodesAPIView.as_view(), name="my_qr_codes"),
]
