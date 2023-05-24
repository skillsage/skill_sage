from models.user import User, Role, JobSeeker, Experience, Skill, JobSeekerSkill
from marshmallow import Schema, fields, validate, ValidationError
from routes.helpers import sendError, sendSuccess
from routes.middlewares import user_authentication
from db.connection import session
from fastapi import APIRouter, Request, Depends, status
from sqlalchemy.orm import subqueryload

import bcrypt
import datetime
import jwt
import os

# new imports fast api
from pydantic import BaseModel

router = APIRouter(
    prefix="/user", tags=["user"], dependencies=[Depends(user_authentication)]
)


@router.get("/")
async def get_user(request: Request):
    print(request.state)
    user = session.query(User).filter(User.id == request.state.user["id"]).first()

    return user.to_json()


class UpdateData(BaseModel):
    about: str | None = None
    location: str | None = None
    education: str | None = None
    portfolio: str | None = None


@router.put("/")
async def update_user(request: Request, data: UpdateData):
    print(request.state)
    seeker = (
        session.query(JobSeeker)
        .filter(JobSeeker.user_id == request.state.user["id"])
        .first()
    )
    seeker.about = data.about
    seeker.location = data.location
    seeker.education = data.education
    seeker.portfolio = data.portfolio
    session.commit()
    return sendSuccess("updated")


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
        res = session.query(Skill).join(JobSeekerSkill).filter(JobSeekerSkill.user_id == request.state.user["id"]).all()
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
        existingSkill = session.query(Skill).filter(Skill.id == skill.id).count()
        if existingSkill > 0:
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
    existingSkill = session.query(Skill).filter(Skill.name == data.name).count()
    if existingSkill:
        sendError("skill already exists")

    sk = Skill(data.name)
    session.add(sk)
    session.commit()

    return sendSuccess("created")
