import requests
from decouple import config

ELEVEN_LABS_API_KEY=config("ELEVEN_LABS_API_KEY")

#eleven labs
#convert text to speech
def convert_text_to_speech(message):
    print("try convert to speech")
    body = {
    "text": message,
    "voice_settings": {
        "stability": 0,
        "similarity_boost": 0
        }
    }

    #define voice
    voice_rachel="21m00Tcm4TlvDq8ikWAM"
    
    headers = { "xi-api-key": ELEVEN_LABS_API_KEY, "Content-Type": "application/json", "accept": "audio/mpeg" }
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_rachel}"
    
    try:
        print("--------------try request post")
        response=requests.post(endpoint,json=body,headers=headers)
    
    except Exception as e:
        print(f"request error {e}")
        
    #handle response
    if response.status_code==200:
        return response.content
    else:
        print(f"status_code {response.status_code}")
        return


if __name__ =="__main__":
    print(ELEVEN_LABS_API_KEY)