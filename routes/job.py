from fastapi import APIRouter, Request, Depends, status, UploadFile, Response
from .middlewares import with_authentication
from models.user import Role
from models.job import Job
from db.connection import session
from pydantic import BaseModel, EmailStr
from .helpers import sendError, sendSuccess
from typing import List, Optional
import datetime

router = APIRouter(
    prefix="/job",
    tags=["job"],
    dependencies=[Depends(with_authentication([Role.JOB_SEEKER, Role.CREATOR, Role.EMPLOYER]))],
)


class JobData(BaseModel):
    id: Optional[int] | None = None
    title: str | None = None
    description: str
    requirements: list[str] | None = None
    skills: list[str] | None = None
    position: str | None = None
    image: str | None = None
    location: str | None = None
    position: str | None = None
    expiry: datetime.date | None = None
    salary: float | None = None
    type: str | None = None


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
        session.add(job)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        print(err)
        return sendError("failed")


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

        session.commit()
        return sendSuccess("Job updated successfully")
    except Exception as err:
        print(err)
        return sendError("Unable to update job")


@router.get("/")
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
                "user_id": job.user_id,
            }
            job_list.append(job_dict)
        return sendSuccess(job_list)
    except Exception as err:
        print(err)
        return sendError("Failed to retrieve jobs")


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
        print(err)
        return sendError("Failed to delete job")
