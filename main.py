#uvicorn main:app
#uvicorn main:app --reload

from typing import Union

from fastapi import FastAPI,File,UploadFile,HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

#Custom function imports
from functions.openai_requests import convert_audio_to_text, get_chat_response,store_messages,reset_messages
from functions.text_to_speech import convert_text_to_speech

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

#check health
@app.get("/reset")
def read_conversation():
    reset_messages()
    return {"message": "reseted file"}


@app.get("/post-audio-get/")
async def get_audio():
    #get saved audio
    audio_input=open("guillem.mp3","rb")
    
    #decode audio
    message_decoded=convert_audio_to_text(audio_input)
    #Guard
    if not message_decoded:
        return HTTPException(status_code=400,detail="Failed to decode Audio")
    
    #get chatgpt response
    chat_response=get_chat_response(message_decoded)
    #Guard
    if not chat_response:
        return HTTPException(status_code=400,detail="Failed to get chat response")
    
    store_messages(message_decoded,chat_response)
    
    #convert chat response to audio
    audio_output=convert_text_to_speech(chat_response)
    #Guard
    if not audio_output:
        return HTTPException(status_code=400,detail="Failed to get audio output")
    
    #creat a generator 
    def iterfile():
        yield audio_output
        
    return StreamingResponse(iterfile(),media_type="audio/mpeg")
        
    
    
    
    return "done"

#post not response
#note: not playing in browser when using post requests
#https://online-voice-recorder.com/
@app.post("/post-audio")
async def post_audio(file: UploadFile = File(...)):
    print("hello "+str(file))
    