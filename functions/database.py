import json
import random


def get_recent_messages():
    file_name="stored_data.json"
    learn_instruction={
        "role":"system",
        "content":"you are interviewing the user for a job as a retail assistant. Ask short questions that are relevant to the junior position. Your name is Rachel. The user is called Will. Keep your answers to under 30 words."
        
    }
    
    #initilize messages
    messages=[]
    
    #add a random element
    x=random.uniform(0,1)
    
    if x<0.5:
        learn_instruction["content"]=learn_instruction["content"]+" Your response will include some dry humour."
    else:
        learn_instruction["content"]=learn_instruction["content"]+" Your response will include a rather challenging question."
        
    #append instruction to message
    messages.append(learn_instruction)
    
    #get last messages
    try:
        with open(file_name) as user_file:
            data=json.load(user_file)
            
            #append last 5 itmes
            if data:
                if (len(data))<5:
                    for item in data:
                        messages.append(item)
                else:
                    for item in data[-5]:
                        messages.append(item)
    except Exception as e:
        pass
    
    return messages