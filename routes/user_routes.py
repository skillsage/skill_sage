from models.user import User, Role, Education, JobSeeker, Experience, Skill, JobSeekerSkill, File, UserResume
from routes.helpers import sendError, sendSuccess, getSha
from routes.middlewares import user_authentication
from db.connection import session
from fastapi import APIRouter, Request, Depends, status, UploadFile, Response
from typing import List, Optional

import datetime
import uuid
import copy
# new imports fast api
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="/user", tags=["user"], dependencies=[Depends(user_authentication)]
)

app_router = APIRouter(
    prefix="/user", tags=["user"],
)


@router.get("/")
async def get_user(request: Request):
    user_id = request.state.user["id"]
    print("user is == ",user_id)
    # user = session.query(User).join(User.profile).join(User.experiences).join(User.education).filter(User.id == user_id).first()
    u = session.query(User).join(User.profile).filter(User.id == user_id).first()
    user = copy.copy(u)
    if user is None:
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

    if user.profile_image is not None:
        img = user.profile_image
        user.profile_image = base_url + "file/"+ img
        # http://localhost:8000/user/file/http://localhost:8000/user/file/b695185f-2d2d-4b7a-b8e1-0ab4dd75f32a.jpg

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
    id: Optional[int] = None
    company_name: str
    job_title: str
    start_date: datetime.date
    end_date: datetime.date | None = None
    is_remote: bool = False
    has_completed: bool = False
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
        exp.has_completed = data.has_completed
        exp.tasks = data.tasks
        session.add(exp)
        session.commit()

        # new_exp = session.query(Experience).filter(Experience.id == exp.id).first()
        return sendSuccess("created")
    except Exception as err:
        print(err)
        sendError("unable to add experience")

@router.delete("/experience/{id}", status_code=200)
async def delete_experience(id: str, request: Request):
    try:
        user_id = request.state.user["id"]
        exp = session.query(Experience).filter(Experience.id == id, Experience.user_id == user_id).first()
        session.delete(exp)
        session.commit()
        return sendSuccess("deleted")
    except Exception as err:
        return sendError("unable to delete experience")


@router.put("/experience", status_code=200)
async def update_experience(request: Request, data: ExperienceData):
    try:
        user_id = request.state.user["id"]
        exp = session.query(Experience).filter(Experience.id == data.id, Experience.user_id == user_id).first()
        if exp is None:
            return sendError("experience not found")
        
        print("data is ", data)
        print("data is ", exp)
        exp.company_name = data.company_name
        exp.job_title = data.job_title
        exp.start_date = data.start_date
        exp.end_date = data.end_date
        exp.is_remote = data.is_remote
        exp.has_completed = data.has_completed
        exp.tasks = data.tasks
        session.commit()
        return sendSuccess("saved")
    except Exception as err:
        print(err)
        sendError("unable to update experience")



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
    name: Optional[str] = None
    about: Optional[str] = None
    location: Optional[str] = None
    portfolio: Optional[str] = None
    languages: Optional[List[str]] = None

@router.put("/profile")
async def update_profile(request: Request, data: UpdateProfile):
    print(data)
    try:
        user = session.query(User).filter(User.id == request.state.user["id"]).first()
        profile = session.query(JobSeeker).filter(
            JobSeeker.id == user.profile_id
        ).first()
        if data.name is not None:
            user.name = data.name
        if data.about is not None:
            profile.about = data.about
        if data.location is not None:
            profile.location = data.location
        if data.portfolio is not None:
            profile.portfolio = data.portfolio
        if data.languages is not None:
            profile.languages = data.languages
       
        session.commit()
        return sendSuccess("Profile updated successfully")

    except Exception as err:
        print(err)
        return sendError("internal server error", 500)

@router.post("/image",status_code=status.HTTP_201_CREATED)
async def upload_image(img: UploadFile, request: Request):
    user_id = request.state.user["id"]
    user = session.query(User).filter(User.id == user_id).first()
    # if user.profile_image is not None:
    #     file_delete = session.query(File).filter(File.filename).first()
    #     session.delete(file_delete)
    # http://143.198.235.166:3000/
    new_file = await img.read()
    fileSha = getSha(new_file)
    ex_chunk = img.filename.split(".")
    ext = ex_chunk[len(ex_chunk)-1:][0]
    filename = str(uuid.uuid4())+"."+ext
    print(filename, ext, sep=" |  " )
    dbImg = File(
            data=new_file,
            filename=filename,
            type=img.content_type,
            sha=fileSha)
    session.add(dbImg)
    user.profile_image = filename

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


class DeleteResume(BaseModel):
    url: str

@router.delete("/resume")
async def remove_resume(request: Request, data: DeleteResume):
    try:
        user_id = request.state.user["id"]
        url = data.url
        chunk = url.split("/")
        filename = chunk[len(chunk)-1:][0]
        print("filename = ", filename)
        resume = session.query(UserResume).filter(UserResume.user_id == user_id, UserResume.filename == filename).first()
        session.delete(resume)
        session.commit()
        # DEL: /user/resume?url=link to the file
        pass
    except Exception as err:
        print(err)
        return sendError("unable to remove resume")

@app_router.get("/file/{filename}")
async def stream_file(filename: str,  request: Request, resp: Response):
    
    try:
        file = session.query(File).filter(File.filename == filename).first()
        if file == None:
            return sendError("file not found")
        return Response(content=file.data, media_type=file.type)
    except Exception as err:
        print(err)
        return sendError("unable to get file", 500)

