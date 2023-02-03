from dataclasses import dataclass
from typing import Optional
from maha.cleaners.functions import normalize, keep
from pprint import pprint


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
    _id: Optional[str] = None

    def dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "filename": self.filename,
            "_id": self._id,
        }

    @property
    def duration(self) -> float:
        return round((self.end - self.start) / 1000, 3)


@dataclass
class MASCAudio:

    filename: str
    text: str
    duration: float
    _id: Optional[str] = None

    def __post_init__(self):
        self.text = normalize(self.text, alef=True)
        self.text = keep(self.text, arabic_letters=True)

    @staticmethod
    def from_audio_segment(audio_segment: AudioSegment):
        return MASCAudio(
            filename=audio_segment.filename,
            text=audio_segment.text,
            duration=audio_segment.duration,
        )

    def dict(self):
        return {
            "filename": self.filename,
            "text": self.text,
            "duration": self.duration,
        }


@dataclass
class Audio:
    """
    Class to represent an audio. which will be converted to AudioDocument.
    """

    audio_id: str
    audio_length: float
    audio_segments: list[AudioSegment]
    _id: Optional[str] = None

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
