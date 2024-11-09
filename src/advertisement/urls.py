from django.urls import path

from advertisement.views import TokenBalanceAPIView, ViewAdvertisementAPIView

urlpatterns = [
    path(
        "view_advertisment/",
        ViewAdvertisementAPIView.as_view(),
        name="view_advertisement",
    ),
    path(
        "get_my_balance/",
        TokenBalanceAPIView.as_view(),
        name="get_user_balance",
    ),
]
