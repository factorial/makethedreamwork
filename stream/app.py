from fastapi import FastAPI, Request,Response, WebSocket
from fastapi.responses import Response, StreamingResponse
import json
import os
import sys
from asgiref.sync import sync_to_async


# Shared code with Django app.
# Add the parent directory of the current script to the module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from team import openai, secrets

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://makethedreamwork.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")

# Set your OpenAI API key
openai.api_key = secrets.OPENAI_API_KEY


# Import django ORM
from django.conf import settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': f"{BASE_DIR}/db.sqlite3",
                }
            },
        INSTALLED_APPS=[
            'team',
            'stream',
            ]
        )
import django
django.setup()
from team import models


@app.get("/generate/{chatid}")
async def generate_text(chatid: str, response: Response):
    # Look up chat
    print (f"models - guid {chatid}")
    chat = await sync_to_async(models.Chat.objects.get)(guid=chatid)
    print('gettin')
    possible_human_role_names = await sync_to_async(list)(chat.human_roles.all().values_list('name', flat=True))
    print(f'possible humans {possible_human_role_names}')

    # If waiting on human input, return nothing.
    print(f'next speaker is {chat.next_speaker_name}')
    if chat.next_speaker_name in possible_human_role_names:
        print('returning empty response')
        return Response("", media_type="text/event-stream")
    
    # Else, generate until waiting on human input, then save the fact we are waiting
    def generate(chat):
        for item in chat.do_one_chat_round():
            yield str(item)

    print('streaming with generate')
    return StreamingResponse(generate(chat), media_type="text/event-stream")

#@app.get("/", response_class=HTMLResponse)
#async def read_root(request: Request):
    #return templates.TemplateResponse("test.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
