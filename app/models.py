from app.database import Base
from sqlalchemy import Column, Integer, String, Date,DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
import enum

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String, nullable=False, default="pending")
    total  = Column(Integer,nullable=False, default=0)
    completed = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    certificates = relationship("Certificate",back_populates="job")

class Certificate(Base):
    __tablename__ = "certificates"

    cert_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    name = Column(String, nullable=False)
    course = Column(String, nullable=False)
    date = Column(Date)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    job = relationship("Job",back_populates="certificates")


import enum
class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"

class CertificateStatus(str,enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"