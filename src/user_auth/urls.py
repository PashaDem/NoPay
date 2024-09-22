from .views import RegisterUserAPIView, LoginUserAPIView
from django.urls import path

urlpatterns = (
    path('register', RegisterUserAPIView.as_view()),
    path('login', LoginUserAPIView.as_view()),
)
