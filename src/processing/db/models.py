from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel



class AudioSegment(BaseModel):
    """
    Class to represent an audio segment.
    start and end are in milliseconds.
    """
    start: int
    end: int
    text: str



@dataclass
class Audio:
    """
    Class to represent an audio. which will be converted to AudioDocument.
    """
    audio_id: str
    audio_segments: list[AudioSegment]
    audio_length: float
