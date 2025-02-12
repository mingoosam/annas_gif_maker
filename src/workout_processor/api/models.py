from pydantic import BaseModel
from typing import List


class ProcessingRequest(BaseModel):
    movements: List[str]
    video_id: str


class GifSegment(BaseModel):
    start_time: float
    end_time: float
    description: str
    similarity_score: float
    gif_path: str


class ProcessingResponse(BaseModel):
    video_id: str
    movements: dict[str, List[GifSegment]] 