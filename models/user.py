# import the Base from the conection.py
from db.connection import Base
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import String, Boolean, LargeBinary, JSON, Enum, ForeignKey, Integer, Date, JSON
from fastapi.encoders import jsonable_encoder
from sqlalchemy.dialects.postgresql import JSONB
from typing import List


class Role(Enum):
    JOB_SEEKER = "JOB_SEEKER"
    EMPLOYER = "EMPLOYER"
    CREATOR = "CREATOR"
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"


class AdminRoles(Enum):
    SYS_MANAGER = "SYS_MANAGER"
    DATA_ADMIN = "DATA_ADMIN"


class User(Base):
    __tablename__ = "users"

    skills = []
    resume = []
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    name = mapped_column(String(), nullable=False)
    email = mapped_column(String(), unique=True, nullable=False)
    password = mapped_column(String(), nullable=False)
    role = mapped_column(String(), nullable=False, default=Role.JOB_SEEKER)
    profile_image = mapped_column(String())
    profile_id = mapped_column(ForeignKey("job_seekers.id"))

    profile: Mapped["JobSeeker"] = relationship("JobSeeker")
    experiences: Mapped[List["Experience"]] = relationship("Experience")
    education: Mapped[List["Education"]] = relationship("Education")

    def __init__(self, name, email, password, role: str):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def to_json(self):
        data = jsonable_encoder(self)
        if "password" in data:
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
    filename = mapped_column(String(), nullable=False)
    type = mapped_column(String(), nullable=False)
    sha = mapped_column(String(), nullable=False)


class SkillFactor(Base):
    __tablename__ = "skill_factors"
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    skill = mapped_column(String(), nullable=False)
    factor = mapped_column(JSONB(), nullable=False)


class Skill(Base):
    __tablename__ = "skills"
    id = mapped_column(Integer(), primary_key=True, nullable=False)
    name = mapped_column(String(), nullable=False)
    lower = mapped_column(String(), nullable=False)

    def __init__(self, name: str):
        self.name = name


class JobSeekerSkill(Base):
    __tablename__ = "job_seeker_skills"

    id = mapped_column(Integer(), primary_key=True, nullable=False)
    skill_id = mapped_column(ForeignKey("skills.id"))
    user_id = mapped_column(ForeignKey("users.id"))

    skill:  Mapped["Skill"] = relationship("Skill")


class Experience(Base):
    __tablename__ = "experiences"

    user_id = mapped_column(Integer(), ForeignKey('users.id'))
    company_name = mapped_column(String(), nullable=False)
    job_title = mapped_column(String(), nullable=False)
    start_date = mapped_column(Date(), nullable=False)
    end_date = mapped_column(Date())
    is_remote = mapped_column(Boolean())
    has_completed = mapped_column(Boolean())
    tasks = mapped_column(String())

    # user: Mapped["User"] = relationship("User")


class Education(Base):
    __tablename__ = "educations"

    user_id = mapped_column(Integer(), ForeignKey('users.id'))
    program = mapped_column(String(), nullable=False)
    institution = mapped_column(String(), nullable=False)
    start_date = mapped_column(Date(), nullable=False)
    end_date = mapped_column(Date())
    has_completed = mapped_column(Boolean())

    def __init__(self):
        pass

    # user: Mapped["User"] = relationship("User")


class JobSeeker(Base):
    __tablename__ = "job_seekers"

    about = mapped_column(String())
    location = mapped_column(String())
    education = mapped_column(String())
    portfolio = mapped_column(String())
    languages = mapped_column(JSON())

    user = relationship("User", back_populates="profile", lazy="select")

    def __init__(self):
        pass

        # return self


class UserResume(Base):
    __tablename__ = "user_resume"
    user_id = mapped_column(ForeignKey("users.id"))
    filename = mapped_column(String())
