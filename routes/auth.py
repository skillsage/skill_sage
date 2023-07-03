from models.user import User, Role, JobSeeker
from marshmallow import Schema, fields, validate, ValidationError
from routes.helpers import sendError, sendSuccess
from db.connection import session
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, validator, EmailStr, constr
import bcrypt

import bcrypt
import datetime
import jwt
import os

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterData(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=6)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, data: RegisterData):
    existing_users = session.query(User).filter(User.email == data.email).count()
    print("existing", existing_users)
    if existing_users:
        sendError("user already exists")

    password = data.password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    user = User(data.name, data.email, hashed_password, Role.JOB_SEEKER)
    try:
        session.add(user)
        session.flush()
        profile = JobSeeker(user_id=user.id)
        session.add(profile)
        session.commit()
    except:
        session.rollback()
        sendError("rolling back")

    return sendSuccess(user.to_json())


class LoginData(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


@auth_router.post("/login")
async def login(request: Request, data: LoginData):
    user = session.query(User).join(JobSeeker).filter(User.email == data.email).first()

    if user is not None:
        if bcrypt.checkpw(data.password.encode("utf-8"), user.password):
            token = jwt.encode(
                {
                    "id": user.id,
                    "seeker_id": user.profile.id,
                    "email": user.email,
                    "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(hours=24),
                },
                os.environ["SECRET_KEY"],
                algorithm="HS256",
            )
            return sendSuccess({"token": token, "user": user.to_json()})
        else:
            sendError("invald credentials"), 400

    sendError("login failed"), 500
