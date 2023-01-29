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
    filename: str

    def dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "filename": self.filename,
        }

    @property
    def duration(self) -> float:
        return round((self.end - self.start) / 1000, 3)


@dataclass
class Audio:
    """
    Class to represent an audio. which will be converted to AudioDocument.
    """

    _id: Optional[str]
    audio_id: str
    audio_segments: list[AudioSegment]
    audio_length: float

    def dict(self):
        return {
            "audio_id": self.audio_id,
            "audio_length": self.audio_length,
            "audio_segments": [segment.dict() for segment in self.audio_segments],
        }

    @staticmethod
    def from_dict(data: dict):
        return Audio(
            _id=data.get("_id"),
            audio_id=data.get("audio_id"),
            audio_length=data.get("audio_length"),
            audio_segments=[
                AudioSegment(**segment) for segment in data.get("audio_segments")
            ],
        )
