from fastapi import APIRouter, Request, Depends, status, UploadFile, Response
from .middlewares import with_authentication
from models.user import Role, UserResume, JobSeekerSkill
from models.job import Job, Bookmark, JobApplication
from models.user import User
from db.connection import session
from pydantic import BaseModel, EmailStr
from .helpers import sendError, sendSuccess
from typing import List, Optional
import datetime

router = APIRouter(
    prefix="/job",
    tags=["job"],
    dependencies=[Depends(with_authentication([Role.EMPLOYER, Role.ADMIN]))],
)

app_router = APIRouter(
    prefix="/job",
    tags=["job"],
    dependencies=[
        Depends(
            with_authentication(
                [Role.CREATOR, Role.ADMIN, Role.JOB_SEEKER, Role.EMPLOYER, Role.ANALYST]
            )
        )
    ],
)


class JobData(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: str
    requirements: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    position: Optional[str] = None
    image: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    expiry: Optional[datetime.date] = None
    salary: Optional[float] = None
    type: Optional[str] = None
    company: Optional[str] = None


class JobApplicationData(BaseModel):
    status: str
    user_id: int
    job_id: int


@router.post("/")
async def post_job(request: Request, data: JobData):
    user_id = request.state.user["id"]
    try:
        job = Job()
        job.title = data.title
        job.requirements = data.requirements
        job.skills = data.skills
        job.description = data.description
        job.image = data.image
        job.user_id = user_id
        job.location = data.location
        job.position = data.position
        job.expiry = data.expiry
        job.salary = data.salary
        job.type = data.type
        job.company = data.company
        session.add(job)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.put("/")
async def update_job(request: Request, data: JobData):
    user_id = request.state.user["id"]
    try:
        job = session.query(Job).filter(Job.id == data.id).first()
        if job is None:
            return sendError("Job not found")

        if job.user_id != user_id:
            return sendError("You do not have permission to update this job")

        # Update the specific fields provided in the request
        if data.title is not None:
            job.title = data.title
        if data.requirements is not None:
            job.requirements = data.requirements
        if data.skills is not None:
            job.skills = data.skills
        if data.description is not None:
            job.description = data.description
        if data.image is not None:
            job.image = data.image
        if data.location is not None:
            job.location = data.location
        if data.position is not None:
            job.position = data.position
        if data.expiry is not None:
            job.expiry = data.expiry
        if data.salary is not None:
            job.salary = data.salary
        if data.type is not None:
            job.type = data.type
        if data.job is not None:
            job.company = data.company

        session.commit()
        return sendSuccess("Job updated successfully")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.get("/")
async def get_jobs():
    try:
        jobs = session.query(Job).all()
        job_list = []
        for job in jobs:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "expiry": job.expiry,
                "salary": job.salary,
                "description": job.description,
                "requirements": job.requirements,
                "image": job.image,
                "type": job.type,
                "position": job.position,
                "skills": job.skills,
                "company": job.company,
                "user_id": job.user_id,
            }
            job_list.append(job_dict)
        return sendSuccess(job_list)
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.delete("/{job_id}")
async def delete_job(job_id: int, request: Request):
    user_id = request.state.user["id"]
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        if job is None:
            return sendError("Job not found")

        if job.user_id != user_id:
            return sendError("You do not have permission to delete this job")

        session.delete(job)
        session.commit()
        return sendSuccess("Job deleted successfully")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.post("/bookmark/{job_id}")
async def create_bookmark(job_id: int, request: Request):
    user_id = request.state.user["id"]
    try:
        job = session.query(Bookmark).filter(Bookmark.job_id == job_id).first()

        if job is not None:
            return sendError("already exists")

        bk = Bookmark()
        bk.user_id = user_id
        bk.job_id = job_id
        session.add(bk)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.get("/bookmarks")
async def get_user_bookmarks(request: Request):
    user_id = request.state.user["id"]
    try:
        bookmarks = (
            session.query(Job).join(Bookmark).filter(Bookmark.user_id == user_id).all()
        )
        bookmark_list = []
        for job in bookmarks:
            bk_dict = {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "expiry": job.expiry,
                "salary": job.salary,
                "description": job.description,
                "requirements": job.requirements,
                "image": job.image,
                "type": job.type,
                "position": job.position,
                "skills": job.skills,
                "company": job.company,
            }
            bookmark_list.append(bk_dict)
        return sendSuccess(bookmark_list)
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.delete("/bookmarks/{job_id}")
async def delete_bookmark(job_id: int, request: Request):
    user_id = request.state.user["id"]
    try:
        bookmark = (
            session.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.job_id == job_id)
            .first()
        )

        if bookmark is None:
            return sendError("not found")

        session.delete(bookmark)
        session.commit()
        return sendSuccess("bookmark removed")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.post("/application/{job_id}")
async def apply_for_job(job_id: int, request: Request):
    user_id = request.state.user["id"]
    try:
        job = (
            session.query(JobApplication)
            .filter(JobApplication.job_id == job_id)
            .first()
        )

        if job:
            return sendError("already applied")

        ap = JobApplication()
        ap.user_id = user_id
        ap.job_id = job_id
        ap.status = "pending"
        session.add(ap)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.get("/applications")
async def get_user_applications(request: Request):
    user_id = request.state.user["id"]
    try:
        applications = (
            session.query(Job, JobApplication.status)
            .join(JobApplication)
            .filter(JobApplication.user_id == user_id)
            .all()
        )
        application_list = []
        for job, status in applications:
            ap_dict = {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "expiry": job.expiry,
                "salary": job.salary,
                "description": job.description,
                "requirements": job.requirements,
                "image": job.image,
                "type": job.type,
                "position": job.position,
                "skills": job.skills,
                "company": job.company,
                "status": status,
            }
            application_list.append(ap_dict)
        return sendSuccess(application_list)
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@app_router.delete("/application/{job_id}")
async def delete_application(job_id: int, request: Request):
    user_id = request.state.user["id"]
    try:
        application = (
            session.query(JobApplication)
            .filter(JobApplication.user_id == user_id, JobApplication.job_id == job_id)
            .first()
        )

        if application is None:
            return sendError("not found")

        session.delete(application)
        session.commit()
        return sendSuccess("application removed")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.get("/applicants")
async def get_applicants(request: Request):
    try:
        applicants = (
            session.query(User, Job, JobApplication.status, UserResume, JobSeekerSkill)
            .join(JobApplication, User.id == JobApplication.user_id)
            .join(Job, Job.id == JobApplication.job_id)
            .join(UserResume, UserResume.user_id == JobApplication.user_id)
            .join(JobSeekerSkill.skill).filter(JobSeekerSkill.user_id == JobApplication.user_id)
            .all()
        )
        applicant_dict = {}
        base_url = request.base_url

        for applicant, job, status, resume, skills in applicants:
            user_id = applicant.id

            if user_id not in applicant_dict:
                applicant_dict[user_id] = {
                    "id": user_id,
                    "skills": [],
                    "resume": [],
                    "name": applicant.name,
                    "email": applicant.email,
                    "experiences": applicant.experiences,
                    "education": applicant.education,
                    "img": applicant.profile_image,
                    "jobs": [],
                }

            job_info = {"job_id": job.id, "job_title": job.title, "status": status}
            if job_info not in applicant_dict[user_id]["jobs"]:
                applicant_dict[user_id]["jobs"].append(job_info)

            resume_url = f"{base_url}file/{resume.filename}"
            applicant_dict[user_id]["resume"].append(resume_url)
            if skills.skill.name not in applicant_dict[user_id]["skills"]:
                applicant_dict[user_id]["skills"].append(skills.skill.name)

        applicant_list = list(applicant_dict.values())

        return sendSuccess(applicant_list)
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.put("/status")
async def update_application_status(data: JobApplicationData):
    try:
        app = (
            session.query(JobApplication)
            .filter(
                JobApplication.user_id == data.user_id,
                JobApplication.job_id == data.job_id,
            )
            .first()
        )
        app.status = data.status
        session.commit()
        return sendSuccess("Status updated")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()
