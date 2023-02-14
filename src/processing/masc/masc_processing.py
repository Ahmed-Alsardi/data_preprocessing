from pathlib import Path
import pandas as pd
from processing.config import Audio, AudioSegment, SourceEnum
from processing.services import folder_vtt_split


def audio_to_dataframe(audios: list[Audio]) -> pd.DataFrame:
    """
    Create a dataframe from a list of Audio objects.
    The dataframe will have the following columns:
    - audio_filename
    - source
        - segment_filename
        - segment_start
        - segment_end
        - segment_text
        - segment_duration
    audio_filename will be used as groupby key.
    Args:
        audios: list of Audio objects
    Returns:
        dataframe
    """
    data = [
        [
            {"audio_filename": audio.filename, **segment.to_dict()}
            for segment in audio.segments
        ]
        for audio in audios
    ]
    data = [item for sublist in data for item in sublist]
    return pd.DataFrame(data)
