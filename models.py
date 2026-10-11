# models.py
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class GradeEnum(str, enum.Enum):
    JUNIOR = "Junior"
    MIDDLE = "Middle"
    SENIOR = "Senior"

class InviteStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class Candidate(Base):
    tablename = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    specialization = Column(String(64), nullable=False)  # Backend, Frontend, Data Science
    confirmed_grade = Column(Enum(GradeEnum), nullable=True)
    last_grade_update = Column(DateTime, default=datetime.utcnow)
    
    # Контакты (скрываются до принятия приглашения)
    email = Column(String(120), nullable=False)
    phone = Column(String(32), nullable=False)
    
    # Стек и опыт
    stack = Column(Text, nullable=False)  # Хранение в виде JSON-массива: ["Python", "PostgreSQL", "FastAPI"]
    experience_years = Column(Float, default=0.0)
    
    # ФСП интеграция
    fsp_id = Column(String(64), nullable=True, index=True)
    fsp_rating = Column(Float, default=0.0)
    fsp_contests_count = Column(Integer, default=0)
    
    # Активность и баллы
    test_score = Column(Float, default=0.0)  # 0-100
    recency_bonus = Column(Float, default=1.0) # бонус за регулярные задачи

    invites = relationship("Invite", back_populates="candidate")

class Vacancy(Base):
    tablename = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    employer_name = Column(String(120), nullable=False)
    title = Column(String(120), nullable=False)
    specialization = Column(String(64), nullable=False)
    required_grade = Column(Enum(GradeEnum), nullable=False)
    required_stack = Column(Text, nullable=False)  # JSON-массив
    
    # Обязательная ЗП по ТЗ
    salary_min = Column(Integer, nullable=False)
    salary_max = Column(Integer, nullable=False)
    currency = Column(String(8), default="RUB")

    invites = relationship("Invite", back_populates="vacancy")

class Invite(Base):
    tablename = "invites"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    
    # Обязательная ЗП в приглашении
    offer_salary_min = Column(Integer, nullable=False)
    offer_salary_max = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    
    status = Column(Enum(InviteStatusEnum), default=InviteStatusEnum.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="invites")
    vacancy = relationship("Vacancy", back_populates="invites")