import asyncio
from asyncio import Task

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model

from qrcode_app.models import QRCodeProcessingStatus
from qrcode_app.serializers import QRCodeProcessingStatusSerializer

User = get_user_model()


def get_notifications_for_user(user: User) -> str:
    qs = QRCodeProcessingStatus.objects.filter(created_by=user, was_seen_by_user=False)
    serialized = QRCodeProcessingStatusSerializer(qs, many=True)
    return serialized.data


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    user: User | None = None
    periodic_task: Task[None] = None

    async def connect(self):
        await self.accept()
        self.user = self.scope["user"]
        notifications = await database_sync_to_async(get_notifications_for_user)(
            self.user
        )
        await self.send_json(notifications, close=False)
        # периодический опрос бд на предмет новых увемлений
        self.periodic_task = asyncio.ensure_future(self.check_new_notifications())

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

    async def receive_json(self, content, **kwargs):
        notification_ids = content["notification_ids"]
        await QRCodeProcessingStatus.objects.filter(id__in=notification_ids).aupdate(
            was_seen_by_user=True
        )

    async def disconnect(self, code):
        self.periodic_task.cancel()
