from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from advertisement.models import Balance
from advertisement.serializers import BalanceSerializer
from advertisement.service import AdvertisementService


@extend_schema_view(
    post=extend_schema(
        summary="Сообщить, что пользователь просмотрел рекламу",
        responses={status.HTTP_200_OK: None},
    )
)
class ViewAdvertisementAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        service = AdvertisementService()
        service.process_advertisement_view(request.user)
        return Response(status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        summary="Возвращает баланс пользователя и его id",
        responses={
            status.HTTP_200_OK: BalanceSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
        },
    )
)
class TokenBalanceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        balance, _ = Balance.objects.get_or_create(user=request.user)
        serializer = BalanceSerializer(balance)
        return Response(serializer.data, status=status.HTTP_200_OK)
