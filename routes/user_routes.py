from models.user import User, Role, JobSeeker, Experience, Skill, JobSeekerSkill, File
from marshmallow import Schema, fields, validate, ValidationError
from routes.helpers import sendError, sendSuccess
from routes.middlewares import user_authentication
from db.connection import session
from fastapi import APIRouter, Request, Depends, status, UploadFile
from sqlalchemy.orm import subqueryload

import bcrypt
import datetime
import jwt
import os

# new imports fast api
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/user", tags=["user"], dependencies=[Depends(user_authentication)]
)


@router.get("/")
async def get_user(request: Request):
    print(request.state)
    user = session.query(User).filter(User.id == request.state.user["id"]).first()

    return user.to_json()


class UpdateUser(BaseModel):
    name: str
    email: EmailStr

@router.put("/profile")
async def update_profile(request: Request, data: UpdateUser):
    try:
        user = session.query(User).filter(User.id == request.state.user["id"]).first()
        user.name = data.name
        user.email = data.email
        session.commit()
        return sendSuccess("profile updated")
    except Exception as err:
        return sendError("internal server error", 500)

class UpdateData(BaseModel):
    about: str | None = None
    location: str | None = None
    education: str | None = None
    portfolio: str | None = None


@router.put("/")
async def update_user(request: Request, data: UpdateData):
    print(request.state)
    try:
        user = request.state.user
        seeker = (
            session.query(JobSeeker).filter(JobSeeker.user_id == user["id"]).first()
        )
        seeker.about = data.about
        seeker.location = data.location
        seeker.education = data.education
        seeker.portfolio = data.portfolio
        session.commit()
        return sendSuccess("updated")
    except Exception as err:
        return sendError("internal server error", 500)


class ExperienceData(BaseModel):
    company_name: str
    job_title: str
    start_date: datetime.date
    end_date: datetime.date | None = None
    is_remote: bool = False
    is_completed: bool = False
    tasks: str | None = None


@router.post("/experience", status_code=status.HTTP_201_CREATED)
async def add_experience(request: Request, data: ExperienceData):
    exp = Experience()
    try:
        exp.user_id = request.state.user["seeker_id"]
        exp.company_name = data.company_name
        exp.job_title = data.job_title
        exp.start_date = data.start_date
        exp.end_date = data.end_date
        exp.is_remote = data.is_remote
        exp.is_completed = data.is_completed
        exp.tasks = data.tasks
        session.add(exp)
        session.commit()

        # new_exp = session.query(Experience).filter(Experience.id == exp.id).first()
        return sendSuccess("created")
    except Exception as err:
        print(err)
        sendError("unable to add experience")


@router.get("/experience")
async def get_experiences(request: Request):
    try:
        res = (
            session.query(Experience)
            .filter(Experience.user_id == request.state.user["seeker_id"])
            .all()
        )
        return sendSuccess(res)
    except:
        sendError("unable fetch experiences", status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/skill")
async def get_skills(request: Request):
    try:
        res = (
            session.query(Skill)
            .join(JobSeekerSkill)
            .filter(JobSeekerSkill.user_id == request.state.user["id"])
            .all()
        )
        # res = session.query(Skill).join(JobSeekerSkill, Job).all()
        return sendSuccess(res)
    except Exception as err:
        print(err)
        return sendError(
            "unable to fetch skills", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# skill model for request body
class SkillData(BaseModel):
    id: int


@router.post("/skill")
async def add_skill(request: Request, skills: list[SkillData]):
    for skill in skills:
        existing_skill = session.query(Skill).filter(Skill.id == skill.id).count()
        if existing_skill > 0:
            sk = JobSeekerSkill()
            sk.skill_id = skill.id
            sk.user_id = request.state.user["seeker_id"]
            session.add(sk)

    session.commit()
    return sendSuccess("skills uploaded")


class SkillCreate(BaseModel):
    name: str


@router.post("/create_skill", status_code=status.HTTP_201_CREATED)
async def create_skill(data: SkillCreate):
    existing_skill = session.query(Skill).filter(Skill.name == data.name).count()
    if existing_skill:
        sendError("skill already exists")

    sk = Skill(data.name)
    session.add(sk)
    session.commit()

    return sendSuccess("created")


# class UpdateProfile(BaseModel):
#     about: str | None = None
#     location: str | None = None
#     education: str | None = None
#     portfolio: str | None = None


# @router.put("/profile", response_model=UpdateProfile)
# async def update_profile(request: Request, data: UpdateProfile):
#     print(data)
#     try:
#         profile = session.query(JobSeeker).filter(
#             JobSeeker.user_id == request.state.user["id"]
#         ).first()
#         profile.about = data.about
#         profile.location = data.location
#         profile.education = data.education
#         profile.portfolio = data.portfolio
#         session.commit()
#         return sendSuccess("profile updated")
#     except Exception as err:
#         print(err)
#         return sendError("internal server error", 500)


@router.post("/upload_resume", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile, request: Request):
    try:
        new_file = await file.read()
        existing_file = (
            session.query(File).filter(File.filename == file.filename).first()
        )
        if existing_file:
            return sendError("file already exist")
        resume = File(
            data=new_file,
            user_id=request.state.user["seeker_id"],
            filename=file.filename,
        )
        session.add(resume)
        session.commit()
        return sendSuccess(f"{file.filename}uploaded")
    except Exception as err:
        print(err)
        return sendError("internal server error", 500)
