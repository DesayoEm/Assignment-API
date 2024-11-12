from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from util import load_file, save_data_in_file, create_user_id
import time
import logging
app=FastAPI()

logging.basicConfig(filename="requests.log",  level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")

async def log_time_taken(request: Request, call_next):
    start = time.perf_counter_ns()
    response = await call_next(request)
    end = time.perf_counter_ns()
    request_time = end-start

    #theres a billion nanoseconds in a second
    seconds = request_time // 1000000000
    #calculate the remaining milliseconds from leftover nanoseconds
    milliseconds = (request_time % 1000000000) // 1000000

    print(f"{request.method} {request.url.path} took {seconds} seconds and {milliseconds} milliseconds")
    logging.info(f"{request.method} {request.url.path} took {seconds} seconds and {milliseconds} milliseconds")

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

users = load_file()
# for id, person in users.items():#Visualise dictionary
#     print(person)

@app.post("/signup", status_code=201)
async def create_user(user: NewUser):
    try:
        if any(person["email"] == user.model_dump()["email"] for id, person in users.items()):
            raise HTTPException(status_code=409,detail="Email already registered")
        user_id = create_user_id()
        users[user_id] = user.model_dump()
        save_data_in_file(users)
        return {"message": "Sign up successful"}

    except ValidationError:
        raise HTTPException(status_code=422)

