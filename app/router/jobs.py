from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
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


@router.get("/{job_id}/", response_model=schemas.JobStatusOut)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
   
    job = db.get(models.Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    progress = (
        (job.completed + job.failed) / job.total
        if job.total > 0
        else 0.0
    )

    #failure list
    failures = [
        schemas.FailureOut(
            cert_id=cert.cert_id,
            name=cert.name,
            error=cert.error_message
        )
        for cert in job.certificates
        if cert.status == "FAILED"
    ]

    #response data
    return schemas.JobStatusOut(
        job_id=job.job_id,
        status=job.status,
        total=job.total,
        completed=job.completed,
        failed=job.failed,
        progress=progress,
        failures=failures
    )