import openai
from decouple import config


#retrieve environtment variables
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

#OPEN AI WHISPER
#CONVERT AUDIO TO TEXT
def convert_audio_to_text(audio_file):
    try:
        transcript=openai.Audio.transcribe("whisper-1",audio_file)
        message_text=transcript["text"]
        return message_text
    except Exception as e:
        print("errror: ",e)
        