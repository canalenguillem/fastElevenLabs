from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from decouple import config
import openai
import shutil
import os
from pydub import AudioSegment

# Custom function imports
from functions.openai_requests import convert_audio_to_text, get_chat_response, store_messages, reset_messages
from functions.text_to_speech import convert_text_to_speech

from functions.audio_processing import convert_wav_to_mp3

# Initialize app
app = FastAPI()

# CORS - origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:3000",
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Check health
@app.get("/health")
def read_root():
    return {"message": "healthy"}

# Reset conversation
@app.get("/reset")
def read_conversation():
    reset_messages()
    return {"message": "reseted file"}

@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    # Save the file temporarily
    temp_file_path = file.filename
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert the audio file to MP3
    mp3_file_path = f"{os.path.splitext(temp_file_path)[0]}.mp3"
    try:
        audio = AudioSegment.from_file(temp_file_path)
        audio.export(mp3_file_path, format="mp3")

        # Open the MP3 file for processing
        audio_input = open(mp3_file_path, "rb")

        # Decode audio
        message_decoded = convert_audio_to_text(audio_input)
        if not message_decoded:
            raise HTTPException(status_code=400, detail="Failed to decode audio")

        # Get chat response
        chat_response = get_chat_response(message_decoded)
        if not chat_response:
            raise HTTPException(status_code=400, detail="Failed chat response")

        store_messages(message_decoded, chat_response)

        # Convert chat response to audio
        audio_output = convert_text_to_speech(chat_response)
        if not audio_output:
            raise HTTPException(status_code=400, detail="Failed audio output")

        # Create a generator that yields chunks of data
        def iterfile():
            yield audio_output

        return StreamingResponse(iterfile(), media_type="audio/mpeg")
    finally:
        # Clean up: remove the temporary files
        # if os.path.exists(temp_file_path):
        #     os.remove(temp_file_path)
        # if os.path.exists(mp3_file_path):
        #     os.remove(mp3_file_path)
        pass
    
    # Endpoint to upload a WAV file and convert it to MP3
@app.post("/upload-wav/")
async def upload_wav(file: UploadFile = File(...)):
    if file.content_type != "audio/wav":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a WAV file.")

    # Save the uploaded WAV file
    temp_wav_path = f"{file.filename}"
    with open(temp_wav_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Convert the WAV file to MP3
        mp3_file_path = convert_wav_to_mp3(temp_wav_path)
        return JSONResponse(content={"message": "File converted successfully", "mp3_file_path": mp3_file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

