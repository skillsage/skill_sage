from models.user import User, Role, Education, JobSeeker, Experience, Skill, JobSeekerSkill, File, UserResume
from routes.helpers import sendError, sendSuccess, getSha
from routes.middlewares import user_authentication
from db.connection import session
from fastapi import APIRouter, Request, Depends, status, UploadFile, Response
from typing import List

import datetime
import uuid
import hashlib
# new imports fast api
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/user", tags=["user"], dependencies=[Depends(user_authentication)]
)


@router.get("/")
async def get_user(request: Request):
    user_id = request.state.user["id"]
    print("user is == ",user_id)
    # user = session.query(User).join(User.profile).join(User.experiences).join(User.education).filter(User.id == user_id).first()
    user = session.query(User).join(User.profile).filter(User.id == user_id).first()
    if user == None:
        return sendError(":lol")
    education = session.query(Education).filter(Education.user_id == user_id).all()
    exp = session.query(Experience).filter(Experience.user_id == user_id).all()
    user.education = education
    user.experience = exp
    user.profile.id
    user.experiences
    user.skills
    user.education

    skills = []
    us = session.query(JobSeekerSkill).join(JobSeekerSkill.skill).filter(JobSeekerSkill.user_id == user_id).all()
    for i in us:
        skills.append(i.skill.name)
    
    base_url =  request.url._url
    resume_links = []
    links = session.query(UserResume).filter(UserResume.user_id == user_id).all()
    for i in links:
        resume_links.append(base_url + "file/"+ i.filename)

    user.skills = skills
    user.resume = resume_links

    if user.profile_image != None:
        user.profile_image = base_url + "file/"+ user.profile_image

    return sendSuccess(user.to_json())


# class UpdateUser(BaseModel):
#     name: str
#     email: EmailStr

# @router.put("/profile")
# async def update_profile(request: Request, data: UpdateUser):
#     try:
#         user = session.query(User).filter(User.id == request.state.user["id"]).first()
#         user.name = data.name
#         user.email = data.email
#         session.commit()
#         return sendSuccess("profile updated")
#     except Exception as err:
#         return sendError("internal server error", 500)


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


class EducationData(BaseModel):
    program: str
    institution: str
    start_date: datetime.date
    end_date: datetime.date | None
    has_completed: bool = False
    
@router.post("/education")
def add_education(request: Request, data: EducationData):
    ed = Education()

    ed.user_id = request.state.user["id"]
    ed.program = data.program
    ed.institution = data.institution
    ed.start_date = data.start_date
    ed.end_date = data.end_date
    ed.has_completed = data.has_completed

    try:
        session.add(ed)
        session.commit()
        return sendSuccess(ed)
    except Exception as err:
        return sendError("unable to add education")


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
    skills: List[int]


@router.post("/skill")
async def add_skill(request: Request, data: SkillData):
    user_id = request.state.user["id"]
    for skill_id in data.skills:
        count = session.query(Skill).filter(Skill.id == skill_id).count()
        if count > 0:
            ext = session.query(JobSeekerSkill).filter(JobSeekerSkill.id == skill_id, JobSeekerSkill.user_id == user_id).count()
            if ext < 1 :
                print("adding ", skill_id, " to ", user_id)
                sk = JobSeekerSkill()
                sk.skill_id = skill_id
                sk.user_id = user_id
                session.add(sk)
    session.commit()
    return sendSuccess("skills uploaded")


class SkillCreate(BaseModel):
    skills: List[str]


@router.post("/create_skill", status_code=status.HTTP_201_CREATED)
async def create_skill(data: SkillCreate):
    for name in data.skills:    
        existing_skill = session.query(Skill).filter(Skill.name == name).count()
        if existing_skill < 1:
            sk = Skill(name)
            session.add(sk)
            session.commit()
        

    return sendSuccess("created")


class UpdateProfile(BaseModel):
    name: str | None
    about: str | None = None
    location: str | None = None
    portfolio: str | None = None
    languages: List[str] | None


@router.put("/profile")
async def update_profile(request: Request, data: UpdateProfile):
    print(data)
    try:
        user = session.query(User).filter(User.id == request.state.user["id"]).first()
        profile = session.query(JobSeeker).filter(
            JobSeeker.id == user.profile_id
        ).first()
        if data.name != None:
            user.name = data.name
        if data.about != None:
            profile.about = data.about
        if data.location != None:
            profile.location = data.location
        if data.portfolio != None:
            profile.portfolio   = data.portfolio
        if data.languages != None:
            profile.languages   = data.languages
        session.commit()

        return sendSuccess("updated")
    except Exception as err:
        print(err)
        return sendError("internal server error", 500)

@router.post("/image",status_code=status.HTTP_201_CREATED)
async def upload_image(img: UploadFile, request: Request):
    user_id = request.state.user["id"]
    user = session.query(User).filter(User.id == user_id).first()
    if user.profile_image != None:
        session.query(File).filter(File.filename).delete()
    new_file = await img.read()
    fileSha = getSha(new_file)
    ex_chunk = img.filename.split(".")
    ext = ex_chunk[len(ex_chunk)-1:][0]
    filename = str(uuid.uuid4())+"."+ext
    img = File(
            data=new_file,
            filename=filename,
            type=img.content_type,
            sha=fileSha)
    session.add(img)
    user.profile_image = img.filename

    session.commit()
    return sendSuccess("uploaded")

    # existing picture
    # yes: delete
    # upload new one


@router.post("/upload_resume", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile, request: Request):
    user_id = request.state.user["id"]
    try:
        new_file = await file.read()
        fileSha = getSha(new_file)
        existing_file = (
            session.query(File).filter(File.sha == fileSha).first()
        )
        ex_chunk = file.filename.split(".")
        ext = ex_chunk[len(ex_chunk)-1:][0]
        filename = str(uuid.uuid4())+"."+ext
        if existing_file:
            return sendError("file already exist")
        resume = File(
            data=new_file,
            filename=filename,
            type=file.content_type,
            sha=fileSha
        )
        session.add(resume)
        session.flush()
        session.add(UserResume(filename=resume.filename,user_id=user_id))
        
        session.commit()
        return sendSuccess(f"{file.filename} uploaded")
    except Exception as err:
        print(err)
        return sendError("Internal Server Error", 500)

@router.get("/file/{filename}")
async def stream_file(filename: str,  request: Request, resp: Response):
    
    try:
        file = session.query(File).filter(File.filename == filename).first()
        if file == None:
            return sendError("file not found")
        return Response(content=file.data, media_type=file.type)
    except Exception as err:
        print(err)
        return sendError("unable to get file", 500)
