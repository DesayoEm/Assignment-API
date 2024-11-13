from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from uuid import uuid4
from data import users
import logging
import time




app=FastAPI()

logging.basicConfig(filename="requests.log",  level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

async def log_time_taken(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    end = time.time()
    request_time = end-start

    seconds = int(request_time)
    #getting the milliseconds part by subtracting the seconds and converting the remainder to milliseconds
    milliseconds = (request_time - seconds) * 1000

    print(f"{request.method} {request.url.path} took {seconds} seconds and {milliseconds:.3f} milliseconds")
    logging.info(f"{request.method} {request.url.path} took {seconds} seconds and {milliseconds:.3f} milliseconds")

    return response

app.middleware("http")(log_time_taken)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class NewUser(BaseModel):
    first_name:str = Field(min_length=2)
    last_name:str = Field(min_length=2)
    age:int = Field(ge=18, le=120)
    email:EmailStr
    height:int = Field(ge=50, le=250, description="Height in centimetres, between 50 and 250")

    @field_validator('email')
    def validate_email(cls,email):
        if "@example" in email:
            raise ValueError("Enter a real email address")
        return email

@app.post("/signup", status_code=201)
async def create_user(user: NewUser):
    try:
        if any(person["email"] == user.model_dump()["email"] for id, person in users.items()):
            raise HTTPException(status_code=409,detail="Email already registered")
        user_id = str(uuid4()).replace('-', '')[:5]
        users[user_id] = user.model_dump()
        return {"message": "Sign up successful"}

    except ValidationError:
        raise HTTPException(status_code=422)

