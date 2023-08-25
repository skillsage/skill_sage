
from db.connection import Base

from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import String, ARRAY, Boolean, LargeBinary, JSON, Enum, ForeignKey, Integer, Date, JSON


class JobType(Enum):
    PART_TIME = "PART_TIME"
    FULL_TIME = "FULL_TIME"


class Job(Base):
    __tablename__ = "jobs"
    title = mapped_column(String(), nullable=False)
    description = mapped_column(String(), nullable=False)
    type = mapped_column(String(), nullable=False)
    position = mapped_column(String(), nullable=False)
    skills = mapped_column(ARRAY(String()))
    user_id = mapped_column(ForeignKey("users.id"))


class Course(Base):
    __tablename__ = "courses"
    user_id = mapped_column(ForeignKey("users.id"))
    title = mapped_column(String(), nullable=False)
    sub_title = mapped_column(String(), nullable=False)
    description = mapped_column(String(), nullable=False)
    language = mapped_column(String())
    requirements = mapped_column(ARRAY(String()), default=[])
    lessons = mapped_column(ARRAY(String()))
    skills = mapped_column(ARRAY(String))
    image = mapped_column(String())
    isActive = mapped_column(Boolean(), default=False)

    items = []


class CourseItem(Base):
    __tablename__ = "course_items"
    course_id = mapped_column(ForeignKey("courses.id"))
    name = mapped_column(String(), nullable=False)


class CourseSession(Base):
    __tablename__ = "course_sesions"
    item_id = mapped_column(ForeignKey("course_items.id"))
    name = mapped_column(String(), nullable=False)
    video = mapped_column(String(), nullable=False)
    time = mapped_column(String())