from datetime import datetime
from pydantic import BaseModel


class DatasetOut(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime

    class Config:
        orm_mode = True
