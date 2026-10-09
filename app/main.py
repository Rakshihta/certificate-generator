from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.router.jobs import router as jobs_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(jobs_router)



