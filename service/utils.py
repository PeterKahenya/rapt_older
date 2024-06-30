import json
import random
import requests
import base64
from config import settings
from celery import Celery
import uuid

def generate_random_string(length:int=6):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', k=length))

def generate_client_id():
    return str(uuid.uuid4())

def generate_client_secret():
    return str(uuid.uuid4())+str(uuid.uuid4())

celery_app = Celery("rapt_tasks", broker=settings.rabbitmq_url)
celery_app.conf.update(task_track_started=True)

@celery_app.task
async def smsleopard_send_sms(phone: str, message: str):
    try:
        phone = phone.strip()
        url = f"{settings.smsleopard_base_url}/sms/send"
        credentials = f"{settings.smsleopard_api_key}:{settings.smsleopard_api_secret}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(credentials.encode()).decode()}"
        }
        body = {
            "source": "smsleopard",
            "destination": [
                {
                    "number": phone
                }
            ],
            "message": message
        }
        response = requests.post(url, data=json.dumps(body), headers=headers)
        print(response,response.json())
        return {"success":True,"message":"SMS Sent successfully"}
        # if response.status_code == 201:
        #     if response.json().get("success"):
        #         return response.json()
        #     else:
        #         return {**response.json(),"message":f"{response.json().get('message')} {str(response.json().get('recipients'))}"}
        # else:
        #     raise Exception(f"{response.status_code} - {response.text}")
    except Exception as e:
        raise e
    
