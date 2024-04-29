import requests
from fastapi import Body, FastAPI, Response, status
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from api.backend_logic import BackendLogic
from cronjob.cronjob import Cronjob
import os
import psycopg

class SubscriptionRequest(BaseModel):
	email: str
	interests: str
    
class UnsubscriptionRequest(BaseModel):
    email: str

app = FastAPI()

backend = BackendLogic(os.environ.get("OPENAI_API_KEY"), os.environ.get("POSTGRES_PASSWORD"))

@app.post("/subscribe", status_code=201)
async def subscribe(item: SubscriptionRequest, response: Response):
    try:
        backend.add_user(item.email, item.interests)
        Cronjob().hackernews_to_mail_flow(daily_flow = False, user_list = [item.email])
    except psycopg.errors.UniqueViolation:
        response.status_code = status.HTTP_409_CONFLICT
    return None

@app.post("/unsubscribe", status_code=204)
async def subscribe(item: UnsubscriptionRequest):
    backend.remove_user(item.email)
    return None
