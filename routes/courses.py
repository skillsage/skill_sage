from fastapi import APIRouter, Request, Depends, status, UploadFile, Response
from .middlewares import with_authentication
from models.user import Role
from models.job import Course, CourseItem, CourseSession
from db.connection import session
from pydantic import BaseModel, EmailStr
from .helpers import sendError, sendSuccess
from typing import List, Optional
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/course",
    tags=["course"],
    dependencies=[
        Depends(with_authentication([Role.JOB_SEEKER, Role.CREATOR, Role.EMPLOYER]))
    ],
)


# - crud course
# - crud course item
# - crud course lession
class CreateCourseData(BaseModel):
    title: str
    sub_title: str
    description: str
    language: str
    requirements: List[str]
    lessons: List[str]
    skills: List[str]
    image: Optional[str] = None
    isActive: bool


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
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.get("/")
async def get_courses(request: Request):
    user_id = request.state.user["id"]
    try:
        courses = (
            session.query(Course)
            .filter(Course.user_id == user_id)
            .outerjoin(CourseItem)  
            .outerjoin(CourseSession) 
            .all()
        )

        course_data = []
        for course in courses:
            course_dict = {
                "id": course.id,
                "title": course.title,
                "sub_title": course.sub_title,
                "description": course.description,
                "requirements": course.requirements,
                "skills": course.skills,
                "image": course.image,
                "items": [],
            }

            for item in course.items:
                item_dict = {
                    "id": item.id,
                    "name": item.name,
                    "sessions": [],  
                }

                for s in item.sessions:
                    session_dict = {
                        "id": s.id,
                        "name": s.name,
                        "video": s.video,
                    }
                    item_dict["sessions"].append(session_dict)

                course_dict["items"].append(item_dict)

            course_data.append(course_dict)

        return sendSuccess(course_data)
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.get("/{course_id}")
async def get_details(request: Request, course_id: int):
    user_id = request.state.user["id"]
    try:
        course = (
            session.query(Course)
            .filter(Course.id == course_id, Course.user_id == user_id)
            .first()
        )

        if not course:
            return sendError("Course not found")

        items = course.items
        data = {
            "course": {
                "title": course.title,
                "sub_title": course.sub_title,
                "requirements": course.requirements,
                "skills": course.skills,
                "lessons": course.lessons,
            },
            "items": [],
        }

        for item in items:
            sessions = item.sessions
            data["items"].append(
                {
                    "name": item.name,
                    "sessions": [
                        {
                            "name": session.name,
                            "video": session.video,
                        }
                        for session in sessions
                    ],
                }
            )

        return sendSuccess(data)

    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.put("/{course_id}")
async def update_course(course_id: int, data: CreateCourseData):
    try:
        course = session.query(Course).filter(Course.id == course_id).first()

        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        if course.title is not None:
            course.title = data.title
        if course.sub_title is not None:
            course.sub_title = data.sub_title
        if course.description is not None:
            course.description = data.description
        if course.language is not None:
            course.language = data.language
        if course.requirements is not None:
            course.requirements = data.requirements
        if course.lessons is not None:
            course.lessons = data.lessons
        if course.skills is not None:
            course.skills = data.skills
        if course.image is not None:
            course.image = data.image
        if course.isActive is not None:
            course.isActive = data.isActive

        session.commit()
        return sendSuccess("Course updated successfully")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.delete("/{course_id}")
async def delete_course(course_id: int):
    try:
        course = session.query(Course).filter(Course.id == course_id).first()

        if course is None:
            raise HTTPException(status_code=404, detail="Course not found")

        session.delete(course)
        session.commit()

        return sendSuccess("Course deleted successfully")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


class CourseItemData(BaseModel):
    course_id: int
    name: str


@router.post("/item")
async def add_item(request: Request, data: CourseItemData):
    user_id = request.state.user["id"]
    try:
        count = (
            session.query(Course)
            .filter(Course.id == data.course_id, Course.user_id == user_id)
            .count()
        )

        if count < 1:
            return sendError("Error")

        item = CourseItem()
        item.name = data.name
        item.course_id = data.course_id
        session.add(item)
        session.commit()
        return sendSuccess("created")
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


class CourseSessionData(BaseModel):
    name: str
    video: str
    time: Optional[str] = None
    item_id: int


@router.post("/session")
async def add_session(request: Request, data: CourseSessionData):
    try:
        user_id = request.state.user["id"]
        c = (
            session.query(Course)
            .join(CourseItem)
            .where(Course.user_id == user_id, CourseItem.id == data.item_id)
            .count()
        )
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
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()


@router.get("/search/{skill}")
async def get_courses_by_skill(skill: str):
    try:
        courses = (
            session.query(Course)
            .filter(
                Course.skills.any(skill) 
            )
            .options(
                joinedload(Course.items)  # Eagerly load the 'items' relationship
                .joinedload(CourseItem.sessions)  # Eagerly load the 'sessions' relationship within 'items'
            )
            .all()
        )

        course_data = []
        for course in courses:
            course_dict = {
                "id": course.id,
                "title": course.title,
                "sub_title": course.sub_title,
                "description": course.description,
                "requirements": course.requirements,
                "skills": course.skills,
                "image": course.image,
                "language": course.language,
                "lessons": course.lessons,
                "items": [],
            }

            for item in course.items:
                item_dict = {
                    "id": item.id,
                    "name": item.name,
                    "sessions": [],  # Initialize sessions list
                }

                for s in item.sessions:
                    session_dict = {
                        "id": s.id,
                        "name": s.name,
                        "video": s.video,
                    }

                    # Append the session data to the 'sessions' list within the 'item' dictionary
                    item_dict["sessions"].append(session_dict)

                # Append the 'item' dictionary to the 'items' list within the 'course' dictionary
                course_dict["items"].append(item_dict)

            course_data.append(course_dict)

        return sendSuccess(course_data)
    except Exception as err:
        session.rollback()
        print(err)
        return sendError(err.args)
    finally:
        session.close()
