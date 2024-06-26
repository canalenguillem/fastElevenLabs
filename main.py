from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,FileResponse
from decouple import config
import openai
import shutil
import os
from pydub import AudioSegment

# Custom function imports
from functions.openai_requests import convert_audio_to_text, get_chat_response, store_messages, reset_messages
from functions.text_to_speech import convert_text_to_speech

from functions.audio_processing import convert_wav_to_mp3,MP3_FOLDER,delete_mp3_file

# Initialize app
app = FastAPI()

# CORS - origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:3000",
    "http://127.0.0.1:5503",
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
    
    
# Endpoint to list all MP3 files
@app.get("/list-mp3s/")
async def list_mp3s():
    try:
        files = [f for f in os.listdir(MP3_FOLDER) if os.path.isfile(os.path.join(MP3_FOLDER, f))]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(MP3_FOLDER, x)), reverse=True)
        return JSONResponse(content={"mp3_files": files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint to delete an MP3 file
@app.delete("/mp3/{filename}")
async def delete_mp3(filename: str):
    try:
        delete_mp3_file(filename)
        return JSONResponse(content={"message": f"File {filename} deleted successfully"})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Endpoint to serve an MP3 file
@app.get("/mp3/{filename}")
async def get_mp3(filename: str):
    file_path = os.path.join(MP3_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='audio/mpeg', filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
    
# Endpoint to convert an MP3 file to text
@app.get("/mp3-to-text/{filename}")
async def mp3_to_text(filename: str):
    file_path = os.path.join(MP3_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with open(file_path, "rb") as audio_input:
            message_decoded = convert_audio_to_text(audio_input)
            if not message_decoded:
                raise HTTPException(status_code=400, detail="Failed to decode audio")
        return JSONResponse(content={"message": "Audio converted to text", "text": message_decoded})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

