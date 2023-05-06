import asyncio
import json
from channels.consumer import AsyncConsumer

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        # When a WebSocket connection is made, send a message to the client
        await self.send({
            "type": "websocket.accept"
        })

        # Add the WebSocket connection to a group named "chat"
        await self.channel_layer.group_add(
            "chat",
            self.channel_name
        )

    async def websocket_receive(self, event):
        # When a message is received over WebSocket, broadcast it to all clients in the "chat" group
        await self.channel_layer.group_send(
            "chat",
            {
                "type": "chat_message",
                "message": event["text"]
            }
        )

    async def websocket_disconnect(self, event):
        # When a WebSocket connection is closed, remove it from the "chat" group
        await self.channel_layer.group_discard(
            "chat",
            self.channel_name
        )

    async def chat_message(self, event):
        # Send a message over WebSocket to all clients in the "chat" group
        await self.send({
            "type": "websocket.send",
            "text": event["message"]
        })

