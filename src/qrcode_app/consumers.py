import asyncio
from asyncio import Task
from logging import getLogger

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import inline_serializer
from drf_spectacular_websocket.decorators import extend_ws_schema
from rest_framework.serializers import CharField

from qrcode_app.models import QRCodeProcessingStatus
from qrcode_app.serializers import (
    QRCodeProcessingStatusSerializer,
    ViewNotificationSerializer,
)

logger = getLogger(__name__)

User = get_user_model()


def get_notifications_for_user(user: User) -> str:
    qs = QRCodeProcessingStatus.objects.filter(created_by=user, was_seen_by_user=False)
    serialized = QRCodeProcessingStatusSerializer(qs, many=True)
    return serialized.data


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    user: User | None = None
    periodic_task: Task[None] = None

    @extend_ws_schema(
        type="send",
        summary="Отправляет список непрочитанных уведомлений для пользователя.",
        request=None,
        responses=QRCodeProcessingStatusSerializer,
    )
    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]
        notifications = await database_sync_to_async(get_notifications_for_user)(
            self.user
        )
        await self.send_json(notifications, close=False)
        # периодический опрос бд на предмет новых увемлений
        self.periodic_task = asyncio.ensure_future(self.check_new_notifications())

    @extend_ws_schema(
        type="send",
        summary="Отправляет новые уведомления каждые n секунд(дефолт-30).",
        responses=QRCodeProcessingStatusSerializer,
    )
    async def check_new_notifications(self):
        while True:
            await asyncio.sleep(settings.NOTIFICATIONS_CHECK_TIMEOUT_SEC)
            new_notifications_count = await (
                QRCodeProcessingStatus.objects.filter(
                    created_by=self.user,
                    was_seen_by_user=False,
                ).acount()
            )

            if new_notifications_count >= 1:
                notifications = await sync_to_async(get_notifications_for_user)(
                    self.user
                )
                await self.send_json(notifications, close=False)

    @extend_ws_schema(
        type="send",
        summary="Помечает уведомления как прочитанные.",
        request=ViewNotificationSerializer,
        responses=inline_serializer(
            name="Сообщение об ошибке", fields={"message": CharField()}
        ),
    )
    async def receive_json(self, content, **kwargs):
        try:
            serializer = ViewNotificationSerializer(data=content)
            serializer.is_valid(raise_exception=True)
        except Exception as err:
            logger.error(err)
            await self.send_json({"message": f"Invalid message format: {err}"})
        else:
            await QRCodeProcessingStatus.objects.filter(
                id__in=serializer.validated_data["notification_ids"]
            ).aupdate(was_seen_by_user=True)

    async def disconnect(self, code):
        self.periodic_task.cancel()
