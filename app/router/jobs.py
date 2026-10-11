from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.processor import process_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/", response_model=schemas.JobCreated, status_code=status.HTTP_202_ACCEPTED)
def create_job(payload: schemas.JobCreate,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    #creating jobs 
    job = models.Job(
        total = len(payload.recipients),
        status = models.JobStatus.PENDING
    )
    db.add(job)
    db.flush()

    #create certificate for each recipients
    for recipient in payload.recipients:
        certificate = models.Certificate(
            job_id=job.job_id,
            name=recipient.name,
            course=recipient.course,
            date=recipient.date,
            status=models.CertificateStatus.PENDING
        )
        db.add(certificate)

    db.commit()
    db.refresh(job)
    background_tasks.add_task(process_job, job.job_id) 
    

    return job