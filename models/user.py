# import the Base from the conection.py
from db.connection import Base
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import String, Boolean, LargeBinary, Enum, ForeignKey, Integer, Date
from fastapi.encoders import jsonable_encoder
from typing import List

class Role(Enum):
    JOB_SEEKER = "JOB_SEEKER"
    EMPLOYER = "EMPLOYER"
    SKIL_DEV_PROVIDER = "SKILL_DEV_PROVIDER"
    SYS_ADMIN = "SYS_ADMIN"
    ANALYST = "ANALYST"


class AdminRoles(Enum):
    SYS_MANAGER = "SYS_MANAGER"
    DATA_ADMIN = "DATA_ADMIN"


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    name = mapped_column(String(), nullable=False)
    email = mapped_column(String(), unique=True, nullable=False)
    password = mapped_column(String(), nullable=False)
    role = mapped_column(String(), nullable=False)

    profile: Mapped["JobSeeker"] = relationship("JobSeeker")

    def __init__(self, name, email, password, role: str):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def to_json(self):
        data = jsonable_encoder(self)
        del data["password"]
        return data


class Employer(Base):
    __tablename__ = "employers"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    user_id = mapped_column(ForeignKey("users.id"))
    company_name = mapped_column(String(), nullable=False)
    contact_info = mapped_column(String(), nullable=False)
    is_verified = mapped_column(Boolean(), default=False)


class File(Base):
    __tablename__ = "files"
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    data = mapped_column(LargeBinary(), nullable=False)
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    filename = mapped_column(String(), nullable=False)


class Skill(Base):
    __tablename__ = "skills"
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    name = mapped_column(String(), nullable=False)

    seekers: Mapped[List["JobSeekerSkill"]] = relationship("JobSeekerSkill")

    def __init__(self, name: str):
        self.name = name


class JobSeekerSkill(Base):
    __tablename__ = "job_seeker_skills"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    skill_id = mapped_column(ForeignKey("skills.id"))
    user_id = mapped_column(ForeignKey("job_seekers.id"))

    skill: Mapped["Skill"] = relationship("Skill",foreign_keys=[skill_id])

    profile: Mapped["JobSeeker"] = relationship("JobSeeker", foreign_keys=[user_id])


class Experience(Base):
    __tablename__ = "experiences"

    user_id = mapped_column(ForeignKey("job_seekers.id"), nullable=False)
    company_name = mapped_column(String(), nullable=False)
    job_title = mapped_column(String(), nullable=False)
    start_date = mapped_column(Date(), nullable=False)
    end_date = mapped_column(Date())
    is_remote = mapped_column(Boolean())
    is_completed = mapped_column(Boolean())
    tasks = mapped_column(String())

    profile: Mapped["JobSeeker"] = relationship()


class JobSeeker(Base):
    __tablename__ = "job_seekers"

    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    about = mapped_column(String())
    location = mapped_column(String())
    education = mapped_column(String())
    resume_id = mapped_column(ForeignKey("files.id"))
    portfolio = mapped_column(String())

    user: Mapped["JobSeeker"] = relationship("User", foreign_keys=[user_id])

    experiences: Mapped[List["Experience"]] = relationship("Experience")

    def __init__(self, user_id):
        self.user_id = user_id


class Course(Base):
    __tablename__ = "courses"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    user_id = mapped_column(ForeignKey("users.id"))
    course_name = mapped_column(String(), nullable=False)
    link_to = mapped_column(String(), nullable=False)
    is_verified = mapped_column(Boolean())


class UserCourse(Base):
    __tablename__ = "user_courses"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    user_id = mapped_column(ForeignKey("users.id"))
    course_id = mapped_column(ForeignKey("courses.id"))


class SysAdminRole(Base):
    __tablename__ = "sys_admin_roles"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    user_id = mapped_column(ForeignKey("users.id"))
    role = mapped_column(String(), nullable=False)
