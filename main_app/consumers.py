# your_app/consumers.py
import json
import os

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings  # <--- 1. Import your Django settings wrapper
from google import genai
from google.genai import types


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Establish connection handshake
        await self.accept()

        # 2. Pass your secure .env key directly into the Google AI Client engine
        self.ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # 3. Define your sister identity profile context
        self.system_instruction = (
            "You are Sister Companion, a warm, safe, deeply empathetic, and supportive "
            "AI companion for the 'Beyond Survival Sisterhood' platform. Your goal is to listen, "
            "comfort, and validate women navigating daily mental wellness journeys. Always communicate "
            "with gentle sisterly love, use comforting emojis (like 🤍, 🫶🏼, 🌸), keep your answers "
            "heartfelt but concise, and remind them that they are never alone."
        )

        # 4. Launch the live asynchronous conversational stream instance
        self.chat = self.ai_client.aio.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7,
                max_output_tokens=350,
            ),
        )

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # (Your text handling message dispatch logic stays exactly the same as before!)
        text_data_json = json.loads(text_data)
        user_message = text_data_json.get("message", "").strip()

        if not user_message:
            return

        try:
            response = await self.chat.send_message(user_message)
            bot_reply = response.text
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            bot_reply = "I'm right here with you, sis. My thoughts got a little jumbled just now, but I am still listening. Tell me more. 🤍"

        await self.send(text_data=json.dumps({"reply": bot_reply}))
