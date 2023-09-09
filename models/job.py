
from db.connection import Base

from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import String, ARRAY, Boolean, LargeBinary, JSON, Enum, ForeignKey, Integer, Date, Float, JSON


class JobType(Enum):
    PART_TIME = "PART_TIME"
    FULL_TIME = "FULL_TIME"


class Job(Base):
    __tablename__ = "jobs"
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    title = mapped_column(String(), nullable=False)
    location = mapped_column(String(), nullable=False)
    expiry = mapped_column(Date(), nullable=False)
    salary = mapped_column(Float(), nullable=False)
    company = mapped_column(String(), nullable=False)
    description = mapped_column(String(), nullable=False)
    requirements = mapped_column(ARRAY(String()))
    image = mapped_column(String())
    type = mapped_column(String(), nullable=False)
    position = mapped_column(String(), nullable=False)
    skills = mapped_column(ARRAY(String()))
    user_id = mapped_column(ForeignKey("users.id"))


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    user_id = mapped_column(Integer(), ForeignKey("users.id"), nullable=False)
    job_id = mapped_column(Integer(), ForeignKey("jobs.id"), nullable=False)


class JobApplication(Base):
    __tablename__ = "job_applications"
    id = mapped_column(Integer(), primary_key=True, index=True)
    user_id = mapped_column(Integer(), ForeignKey("users.id"), nullable=False)
    job_id = mapped_column(Integer(), ForeignKey("jobs.id"), nullable=False)
    status = mapped_column(String(), nullable=False)  # e.g., "pending," "accepted," "rejected"
    # Add more fields as needed

class Course(Base):
    __tablename__ = "courses"
    user_id = mapped_column(ForeignKey("users.id"))
    title = mapped_column(String(), nullable=False)
    sub_title = mapped_column(String(), nullable=False)
    description = mapped_column(String(), nullable=False)
    language = mapped_column(String())
    requirements = mapped_column(ARRAY(String()), default=[])
    lessons = mapped_column(ARRAY(String()))
    skills = mapped_column(ARRAY(String()))
    image = mapped_column(String())
    isActive = mapped_column(Boolean(), default=False)
    items = relationship("CourseItem", back_populates="course")
    # items = []


class CourseItem(Base):
    __tablename__ = "course_items"
    course_id = mapped_column(ForeignKey("courses.id"))
    name = mapped_column(String(), nullable=False)
    course = relationship("Course", back_populates="items")


class CourseSession(Base):
    __tablename__ = "course_sessions"
    item_id = mapped_column(ForeignKey("course_items.id"))
    name = mapped_column(String(), nullable=False)
    video = mapped_column(String(), nullable=False)
    time = mapped_column(String())
