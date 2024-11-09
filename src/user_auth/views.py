import rest_framework.serializers as serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from user_auth.serializers import RegisterUserSerializer, UserLoginSerializer

User = get_user_model()


class RegisterUserAPIView(APIView):
    serializer_class = RegisterUserSerializer

    @extend_schema(
        summary="Регистрация пользователя.",
        tags=["Authorization, Authentication and User Info"],
        request=RegisterUserSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="Информация о пользователе и токен",
                fields={
                    "user_id": serializers.IntegerField(),
                    "access_token": serializers.CharField(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: None,
        },
    )
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=True)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            data={"user_id": user.id, "access_token": token.key},
            status=status.HTTP_201_CREATED,
        )


class LoginUserAPIView(APIView):
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="Логин пользователя.",
        tags=["Authorization, Authentication and User Info"],
        request=RegisterUserSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="Информация о пользователе и токен",
                fields={
                    "user_id": serializers.IntegerField(),
                    "access_token": serializers.CharField(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Такого пользователя не существует."
            ),
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.validated_data["username"])

        if user.check_password(serializer.validated_data["password"]):
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "user_id": user.id,
                    "token": token.key,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                "Такого пользователя не существует.",
                status=status.HTTP_400_BAD_REQUEST,
            )
