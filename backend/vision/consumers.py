import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class LogConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.user = None

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'user_{self.user.id}_logs'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected for user: {self.user.username}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WebSocket disconnected for user: {self.user.username}")

    async def receive(self, **kwargs):
        """
        Receives messages from the WebSocket client.
        Currently used to handle heartbeat pings.
        """
        try:
            data = json.loads(kwargs['text_data'])
            if data.get('type') == 'heartbeat':
                logger.debug(f"Heartbeat received from user: {self.user.username}")
        except json.JSONDecodeError:
            logger.warning(f"Received invalid JSON from user: {self.user.username}")

    async def log_message(self, event):
        message = event['message']
        prefix = event['prefix']

        await self.send(text_data=json.dumps({
            'message': f"{prefix}: {message}"
        }))
