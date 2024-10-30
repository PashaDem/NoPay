from django.urls import path

from .views import ViewAdvertisementAPIView

urlpatterns = [
    path(
        "view_advertisment/",
        ViewAdvertisementAPIView.as_view(),
        name="view_advertisement",
    ),
]
