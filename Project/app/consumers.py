import json
import speech_recognition as sr
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class VoiceRecognitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if "audio_data" in data:
            text = await self.process_audio(data["audio_data"])
            await self.send(json.dumps({"transcription": text}))

    async def process_audio(self, audio_path):
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(audio_path)

        with audio_file as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_sphinx(audio_data)  # Offline method
        except sr.UnknownValueError:
            text = "Sorry, could not understand."
        except sr.RequestError:
            text = "Speech recognition service is unavailable."

        return text
