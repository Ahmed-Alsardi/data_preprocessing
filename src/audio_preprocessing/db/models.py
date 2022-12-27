from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed


class AudioSegment(BaseModel):
    """
    Class to represent an audio segment.
    start and end are in milliseconds.
    """
    start: int
    end: int
    text: str


class AudioDocument(Document):
    audio_id: Indexed(str)
    audio_segments: list[AudioSegment]


DOCUMENT_LIST = [AudioDocument]
