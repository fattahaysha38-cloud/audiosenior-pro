import os
from fastapi import FastAPI, WebSocket
from faster_whisper import WhisperModel
import yt_dlp

app = FastAPI()
model = WhisperModel("base", device="cpu", compute_type="int8")

def download_audio(url):
    opts = {'format': 'm4a/bestaudio', 'outtmpl': 'audio.%(ext)s', 
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return "audio.mp3"

@app.websocket("/ws/transcrever")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        url = await websocket.receive_text()
        await websocket.send_json({"status": "Iniciando modo ilimitado..."})
        audio_file = download_audio(url)
        segments, _ = model.transcribe(audio_file)
        results = [{"start": s.start, "text": s.text} for s in segments]
        await websocket.send_json({"progress": 100, "status": "Concluído!", "segments": results})
    except Exception as e:
        await websocket.send_json({"error": str(e)})
