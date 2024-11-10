from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework import status

User = get_user_model()


class AuthTokenMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = None
        for header_name, header_value in scope["headers"]:
            if header_name == b"authorization":
                token = header_value.decode()
                break

        user_obj = None
        if not token:
            scope["user"] = AnonymousUser()
            await send(
                {
                    "type": "websocket.disconnect",
                    "text": {
                        "code": status.HTTP_401_UNAUTHORIZED,
                        "reason": "No auth credentials.",
                    },
                }
            )
            return
        else:
            token_val = token.split(" ")[1]
            user_obj = await User.objects.filter(auth_token__key=token_val).afirst()

        if not user_obj:
            scope["user"] = AnonymousUser()
            await send(
                {
                    "type": "websocket.disconnect",
                    "text": {
                        "code": status.HTTP_401_UNAUTHORIZED,
                        "reason": "Invalid auth token",
                    },
                }
            )
            return
        else:
            scope["user"] = user_obj
        return await super().__call__(scope, receive, send)
