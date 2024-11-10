from channels.consumer import AsyncConsumer


class NotificationConsumer(AsyncConsumer):
    async def websocket_connect(self, message):
        await self.send(
            {
                "type": "websocket.accept",
            }
        )
        await self.send(
            {
                "type": "websocket.send",
                "text": f"{self.scope['headers']} is not authentication =(",
            }
        )

    async def websocket_receive(self, message):
        await self.send({"type": "websocket.send", "text": "here!"})

    async def websocket_disconnect(self, message):
        ...
