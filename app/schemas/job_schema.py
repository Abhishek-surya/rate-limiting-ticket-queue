from pydantic import BaseModel

class SubmitJobRequest(BaseModel):
    user_id: str
    payload: str
    idempotency_key: str


class JobStatusResponse(BaseModel):
    job_id: int
    state: str
    result: str | None = None
    error_message: str | None = None

    class Config:
        orm_mode = True   
