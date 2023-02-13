from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SourceEnum(Enum):
    """Source of audio file."""
    MASC: str = "MASC"
    SADA: str = "SADA"


@dataclass
class AudioSegment:
    """
    Audio segment configuration class.
    """
    start: float
    end: float
    text: str
    source: SourceEnum
    filename: str = None

    @property
    def duration(self) -> float:
        return self.end - self.start
    
    def to_dict(self):
        return dict(
            filename=self.filename,
            text=self.text,
            duration=self.duration,
            source=self.source.value,
        )


@dataclass
class Audio:
    """
    Audio configuration class. Used when the audio file is large and needs to be split into segments.
    Will be used when splitting audio based on transcription file, then each segment will be processed
    separately.
    """
    filename: str
    duration: float
    source: SourceEnum
    segments: list[AudioSegment]
