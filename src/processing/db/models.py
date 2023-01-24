from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel



@dataclass
class AudioSegment:
    """
    Class to represent an audio segment.
    start and end are in milliseconds.
    """
    start: int
    end: int
    text: str

    def dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text
        }


@dataclass
class Audio:
    """
    Class to represent an audio. which will be converted to AudioDocument.
    """
    audio_id: str
    audio_segments: list[AudioSegment]
    audio_length: float

    def dict(self):
        return {
            "audio_id": self.audio_id,
            "audio_length": self.audio_length,
            "audio_segments": [segment.dict() for segment in self.audio_segments]
        }
