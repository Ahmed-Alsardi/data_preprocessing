from pathlib import Path
import pandas as pd
from processing.config import Audio, AudioSegment, SourceEnum
from processing.services import folder_vtt_split, clean_text


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


def vtt_split_to_dataframe(
    subtitle_folder: Path, 
    dataframe_path: Path, 
    clean_text: bool = True,
    min_duration=6.0,
    max_duration=16.0,
    threshold=2.0,
    source=SourceEnum.MASC,
) -> pd.DataFrame:
    """
    Take a dataframe and subtitle folder and split the subtitle files into segments.
    The structure of the dataframe should be:
    - audio_filename
    - source
        - segment_filename
        - segment_start
        - segment_end
        - segment_text
        - segment_duration
    audio_filename will be used as groupby key.
    Args:
        subtitle_folder: folder containing subtitle files
        dataframe_path: path to dataframe
        clean_text: clean text using clean_text function
    Returns:
        dataframe
    """
    if dataframe_path.is_dir():
        raise ValueError("dataframe_path should be a path to a file.")
    if dataframe_path.stem != "parquet":
        raise ValueError("dataframe_path should be a parquet file.")
    if not subtitle_folder.is_dir():
        raise ValueError("subtitle_folder should be a path to a folder.")
    audios = folder_vtt_split(
        vtt_folder=subtitle_folder,
        min_duration=min_duration,
        max_duration=max_duration,
        threshold=threshold,
        source=source,
    )
    df = audio_to_dataframe(audios)
    if clean_text:
        df["segment_text"] = df["segment_text"].apply(clean_text)
    df.to_parquet(dataframe_path)
    return df


