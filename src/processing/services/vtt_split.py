from pathlib import Path 
from processing.config import Audio, AudioSegment, SourceEnum

def vtt_split(
    vtt_path: Path,
    min_duration: float = 8.0,
    max_duration: float = 12.0,
    threshold: float = 2.0,
    source: SourceEnum = SourceEnum.MASC,
) -> Audio:
    pass
