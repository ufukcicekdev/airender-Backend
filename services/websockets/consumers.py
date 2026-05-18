import json

from channels.generic.websocket import AsyncWebsocketConsumer


class RenderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.group_name = f"render_{self.task_id}"

        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"type": "connected", "task_id": self.task_id}
            )
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def render_update(self, event):
        await self.send(text_data=json.dumps(event["payload"]))
