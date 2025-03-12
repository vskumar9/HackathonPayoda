import json
import speech_recognition as sr
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from concurrent.futures import ThreadPoolExecutor

# class VoiceRecognitionConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.recognizer = sr.Recognizer()
#         self.executor = ThreadPoolExecutor(max_workers=1)  # For running sync code in async context
#         self.listening_task = None
#         self.should_listen = False

#     async def connect(self):
#         await self.accept()
#         self.should_listen = True
#         # Start listening in the background when the WebSocket connects
#         self.listening_task = asyncio.create_task(self.start_listening())

#     async def disconnect(self, close_code):
#         self.should_listen = False
#         if self.listening_task:
#             self.listening_task.cancel()
#         self.executor.shutdown(wait=False)

#     async def receive(self, text_data):
#         # Optional: Handle any client messages if needed (e.g., start/stop commands)
#         data = json.loads(text_data)
#         if "command" in data and data["command"] == "stop":
#             self.should_listen = False

#     async def start_listening(self):
#         """Continuously listen for speech and send transcriptions."""
#         with sr.Microphone() as source:
#             self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Calibrate for noise
#             await self.send(json.dumps({"status": "Listening started"}))

#             while self.should_listen:
#                 try:
#                     # Run the blocking listen call in a thread
#                     loop = asyncio.get_running_loop()
#                     audio = await loop.run_in_executor(
#                         self.executor,
#                         lambda: self.recognizer.listen(
#                             source,
#                             timeout=1,  # Wait 1 sec for speech to start
#                             phrase_time_limit=5  # Stop after 5 sec of speech
#                         )
#                     )
#                     # Process the audio in another thread
#                     text = await loop.run_in_executor(
#                         self.executor,
#                         self.recognize_audio,
#                         audio
#                     )
#                     # Send the transcription to the client
#                     await self.send(json.dumps({"transcription": text}))

#                 except sr.WaitTimeoutError:
#                     # No speech detected within timeout; continue listening
#                     continue
#                 except Exception as e:
#                     await self.send(json.dumps({"error": str(e)}))
#                     break

#             await self.send(json.dumps({"status": "Listening stopped"}))

#     def recognize_audio(self, audio):
#         """Recognize audio synchronously (called in executor)."""
#         try:
#             text = self.recognizer.recognize_sphinx(audio)  # Offline recognition
#             return text
#         except sr.UnknownValueError:
#             return "Sorry, could not understand."
#         except sr.RequestError:
#             return "Speech recognition service is unavailable."


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VoiceRecognitionConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcription = ""

    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"status": "Connected", "transcription": self.transcription}))

    async def disconnect(self, close_code):
        await self.send(json.dumps({"status": "Disconnected"}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if "audio_data" in data:
            new_text = data["audio_data"].strip()
            if self.transcription:
                self.transcription += " " + new_text
            else:
                self.transcription = new_text
            await self.send(json.dumps({"transcription": self.transcription}))
        elif "command" in data and data["command"] == "stop":
            await self.send(json.dumps({"status": "Stopped"}))