from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/", response_model=schemas.JobCreated, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: schemas.JobCreate, db: Session = Depends(get_db)):

    #creating jobs 
    job = models.Job(
        total = len(payload.recipients),
        status = models.JobStatus.PENDING
    )
    db.add_all(job)
    db.flush()

    #create certificate for each recipients
    for recipient in payload.recipients:
        certificate = models.Certificate(
            job_id=job.job_id,
            name=recipient.name,
            course=recipient.course,
            date=recipient.date,
            status=models.JobStatus.PENDING
        )
        db.add(certificate)

    db.commit()
    db.refresh(job)

    return job