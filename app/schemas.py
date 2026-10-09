from datetime import date
from pydantic import BaseModel, Field, ConfigDict

class RecipientIn(BaseModel):
    name: str
    course: str
    date : date

class JobCreate(BaseModel):
    recipients: list[RecipientIn] = Field(min_length=1, max_length=1000)
    # Why cap it at 1000? Write your answer as a README note.

class JobCreated(BaseModel):
    model_config = ConfigDict(from_attributes=True)  
    job_id: int      
    status: str
    total: int