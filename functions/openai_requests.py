import openai
from decouple import config
from functions.database import get_recent_messages
import json



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
        
        
#open AI chatgpt
#get responses to our messages
def get_chat_response(message_input):
    messages=get_recent_messages()
    user_message={"role":"user","content":message_input}
    messages.append(user_message)
    print(messages)
    
    try:
        response=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        print(response)
        message_text=response["choices"][0]["message"]["content"]
        return message_text
    except Exception as e:
        print(e)
        return
    
def store_messages(request_message,response_message):
    #define de file name
    file_name="stored_data.json"
    
    #get recent messages
    messages=get_recent_messages()[1:]
    
    #add messages to data
    user_message={"role":"user","content":request_message}
    assistant_message={"role":"assistant","content":response_message}
    messages.append(user_message)
    messages.append(assistant_message)
    
    #save the updated file
    with open(file_name,"w") as f:
        json.dump(messages,f)
        
def reset_messages():
    #overwrite
    print("overwriting")
    open("stored_data.json","w")
    
    
        