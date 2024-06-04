#uvicorn main:app
#uvicorn main:app --reload

from typing import Union

from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

#Custom function imports
from functions.openai_requests import convert_audio_to_text

#initialize app
app = FastAPI()

#CORS - origins
origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:3000",
]

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#check health
@app.get("/health")
def read_root():
    return {"message": "healthy"}


@app.get("/post-audio-get/")
async def get_audio():
    #get saved audio
    audio_input=open("voice.mp3","rb")
    
    #decode audio
    message_decoded=convert_audio_to_text(audio_input)
    print(message_decoded)
    
    return "done"

#post not response
#note: not playing in browser when using post requests
#https://online-voice-recorder.com/
@app.post("/post-audio")
async def post_audio(file: UploadFile = File(...)):
    print("hello "+str(file))