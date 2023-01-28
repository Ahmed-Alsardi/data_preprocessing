from pathlib import Path
from dataclasses import dataclass
from typing import Generator, Tuple, Optional
import pandas as pd


@dataclass
class AudioSegment:
    filename: str
    start: float
    end: float
    text: str

@dataclass
class AudioFile:
    filename: str
    duration: float
    segments: list[AudioSegment]


ROOT_PATH = Path("~/dev/sada/").expanduser()

def combine_df_rows(df: pd.DataFrame, min_length=20) -> Generator[AudioFile, None, None]:
    """
    Combine rows of a dataframe to increase the length of the audio file
    Args:
        df: DataFrame
        min_length: minimum length of the audio file in seconds
    Returns:
        list of AudioFile objects
    """
    duration = 0
    segments = []
    for _, row in df.iterrows():
        filename = row["FileName"]
        start = row["SegmentStart"]
        end = row["SegmentEnd"]
        text = row["ProcessedText"]
        duration += end - start
        segments.append(AudioSegment(filename, start, end, text))
        if duration >= min_length:
            yield AudioFile(filename, duration, segments)
            duration = 0
            segments = []



if __name__ == "__main__":
    print(ROOT_PATH.exists())
