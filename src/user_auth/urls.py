from django.urls import path

from user_auth.views import LoginUserAPIView, RegisterUserAPIView

urlpatterns = (
    path("register", RegisterUserAPIView.as_view()),
    path("login", LoginUserAPIView.as_view()),
)
