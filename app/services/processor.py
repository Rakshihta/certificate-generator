import os
from datetime import datetime
from app.database import SessionLocal
from app import models
from app.services.pdf import generate_certificate

import logging
logger = logging.getLogger(__name__)

OUTPUT_DIR = "generated"

def process_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.get(models.Job, job_id)
        job.status = models.JobStatus.PROCESSING
        db.commit()

        os.makedirs(f"{OUTPUT_DIR}/{job_id}", exist_ok=True)

        for cert in job.certificates:
            try:
                path = f"{OUTPUT_DIR}/{job_id}/{cert.cert_id}.pdf"

                generate_certificate(
                    cert.name,
                    cert.course,
                    cert.date.strftime("%d %b %Y"),
                    path
                )
                cert.status = models.CertificateStatus.SUCCESS
                cert.file_path = path
                job.completed += 1
               
            except ValueError as e:
                # Expected failure: invalid data
                cert.status = models.CertificateStatus.FAILED
                cert.error_message = str(e)
                job.failed += 1

            except Exception:
                # Unexpected failure: keep the message safe for users
                
                logger.exception("Unexpected error for certificate %s", cert.cert_id)
                cert.status = models.CertificateStatus.FAILED
                cert.error_message = "Certificate generation failed due to an unexpected error."
                job.failed += 1

            job.finished_at = datetime.utcnow()
            db.commit()


        if job.failed == 0:
            job.status = models.JobStatus.COMPLETED
        else:
            job.status = models.JobStatus.COMPLETED_WITH_ERRORS

        db.commit()
    finally:
        db.close()