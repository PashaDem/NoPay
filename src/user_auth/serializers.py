from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
#
# from django.contrib.auth.models import User


class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
