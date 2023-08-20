from fastapi import APIRouter, Request, Depends, status, UploadFile, Response
from .middlewares import with_authentication
from models.user import Role
from models.job import Job, Course, CourseItem, CourseSession
from db.connection import session
from pydantic import BaseModel, EmailStr
from .helpers import sendError, sendSuccess
from typing import List

router = APIRouter(prefix="/course", tags=["course"], dependencies=[
                   Depends(with_authentication([Role.CREATOR]))])


# - crud course
# - crud course item
# - crud course lession
class CreateCourseData(BaseModel):
    title: str
    sub_title: str
    description: str
    language: str
    requirements: list[str]
    lessons: list[str]
    skills: list[str]
    image: str | None


@router.post("/")
async def create_post(request: Request, data: CreateCourseData):
    user_id = request.state.user["id"]

    try:
        course = Course()
        course.user_id = user_id
        course.title = data.title
        course.sub_title = data.sub_title
        course.language = data.language
        course.requirements = data.requirements
        course.lessons = data.lessons
        course.skills = data.skills
        course.description = data.description
        course.image = data.image
        session.add(course)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        print(err)
        return sendError("failed")


@router.get("/")
async def get_courses(request: Request):
    user_id = request.state.user["id"]
    data = session.query(Course).filter(Course.user_id == user_id).all()
    return data


@router.get("/{course_id}")
async def get_details(request: Request, course_id: int):
    user_id = request.state.user["id"]
    try:
        course = session.query(Course).filter(
            Course.id == course_id, Course.user_id == user_id).first()
        data: list[map[str: any]] = []
        items = session.query(CourseItem).filter(
            CourseItem.course_id == course.id).all()

        for i in items:
            s = session.query(CourseSession).filter(
                CourseSession.item_id == i.id).all()
            data.append({
                "name": i.name,
                "sessions": list(map(lambda x: {
                    "name": x.name,
                    "video": x.video,
                }, s))
            })
        course.items = data

        return sendSuccess(course)

    except:
        return sendError("Error")


class CourseItemData(BaseModel):
    course_id: int
    name: str


@router.post("/item")
async def add_item(request: Request, data: CourseItemData):
    user_id = request.state.user["id"]
    try:
        count = session.query(Course).filter(
            Course.id == id, Course.user_id == user_id).count()
        if count < 1:
            return sendError("Error")

        item = CourseItem()
        item.name = data.name
        item.course_id = data.course_id
        session.add(item)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        print(err)
        return sendError("failed")


class CourseSessionData(BaseModel):
    name: str
    video: str
    time: str | None
    item_id: int


@router.post("/session")
async def add_session(request: Request, data: CourseSessionData):
    try:
        user_id = request.state.user["id"]
        c = session.query(Course).join(CourseItem).where(
            Course.user_id == user_id, CourseItem.id == data.item_id).count()
        if c < 1:
            return sendError("item not found")

        s = CourseSession()
        s.name = data.name
        s.video = data.video
        s.time = data.time
        s.item_id = data.item_id
        session.add(s)
        session.commit()
        return sendSuccess("created")
    except:
        return sendError("failed")
