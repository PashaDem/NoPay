from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer, UserLoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from django.db import transaction
User = get_user_model()

class RegisterUserAPIView(APIView):
    serializer_class = RegisterUserSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=True)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            data={'user_id': user.id, 'access_token': token.key},
            status=status.HTTP_201_CREATED,
        )


class LoginUserAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=serializer.validated_data['username'])

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
