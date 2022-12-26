from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed


class AudioSubSegment(BaseModel):
    """
    Class to represent an audio segment.
    start and end are in milliseconds.
    """
    start: int
    end: int
    text: str


class AudioSegments(Document):
    audio_id: Indexed(str)
    audio_segments: list[AudioSubSegment]
