from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.serializers import CharField, ModelSerializer, Serializer

User = get_user_model()


class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password")

    def save(self, **kwargs):
        hashed_password = make_password(self.validated_data["password"])
        return super().save(
            **(kwargs | {"password": hashed_password, "is_active": True})
        )


class UserLoginSerializer(Serializer):
    username = CharField()
    password = CharField()
