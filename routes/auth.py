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
    try:
        existing_users = session.query(User).filter(
            User.email == data.email).count()
        print("existing", existing_users)
        if existing_users:
            return sendError("user already exists")

        password = data.password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        print(hashed_password)
        user = User(data.name, data.email, bytes.decode(
            hashed_password, "utf-8"), Role.JOB_SEEKER)
        try:
            profile = JobSeeker()
            session.add(profile)
            session.flush()
            user.profile_id = profile.id
            session.add(user)
            session.commit()
        except:
            session.rollback()
            sendError("rolling back")
        finally: 
            session.close()
        return sendSuccess(user)
    except Exception as err:
        return sendError(err.args)


class LoginData(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


@auth_router.post("/login")
async def login(request: Request, data: LoginData):
    try:
        user = session.query(User).join(JobSeeker).filter(
            User.email == data.email).first()
        if user is None:
            return sendError("not found")

        user = session.query(User).join(JobSeeker).filter(
            User.email == data.email).first()

        print("user is ", user.password)
        if user is not None:
            if bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
                token = generate_token(
                    {
                        "id": user.id,
                        "seeker_id": user.profile.id,
                        "email": user.email,
                        "role": user.role,
                        "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                        + datetime.timedelta(hours=24),
                    })
                return sendSuccess({"token": token, "user": user.to_json()})
            else:
                return sendError("invalid credentials", 400)
    except Exception as err:
        return sendError(err.args)


def generate_token(data):
    return jwt.encode(
        data,
        os.environ["SECRET_KEY"],
        algorithm="HS256",
    )
