from pathlib import Path
import logging
import pandas as pd
from processing.config import Audio, SourceEnum
from processing.services import folder_vtt_split, clean_text


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


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
    clean_segment_text: bool = True,
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
    if dataframe_path.suffix != ".parquet":
        raise ValueError("dataframe_path should be a parquet file.")
    if not subtitle_folder.is_dir():
        raise ValueError("subtitle_folder should be a path to a folder.")
    logging.info("Start splitting subtitle files into segments.")
    audios = folder_vtt_split(
        vtt_folder=subtitle_folder,
        min_duration=min_duration,
        max_duration=max_duration,
        threshold=threshold,
        source=source,
    )
    df = audio_to_dataframe(audios)
    logging.info("Converting audio segments to dataframe.")
    if clean_segment_text:
        logging.info("Cleaning text.")
        df["segment_text"] = df["segment_text"].apply(clean_text)
    df.source = pd.Categorical(df.source)
    df.audio_filename = df.audio_filename.apply(lambda x: x.replace(".ar", ""))
    df.segment_filename = df.segment_filename.apply(lambda x: x.replace(".ar", ""))
    logging.info("Saving dataframe to parquet file.")
    df.to_parquet(dataframe_path)
    return df


def validate_dataframe(
    df: pd.DataFrame, min_duration: float = 6.0, max_duration: float = 16.0
) -> pd.Series:
    """
    validate dataframe segments duration
    ensure that the duration between min_duration and max_duration
    Args:
        df: dataframe
        min_duration: minimum duration
        max_duration: maximum duration
    Returns:
        Series describing the segment duration
    """
    if df.segment_duration.min() < min_duration:
        raise ValueError(f"min duration is {df.segment_duration.min()}")
    if df.segment_duration.max() > max_duration:
        raise ValueError(f"max duration is {df.segment_duration.max()}")
    return df.segment_duration.describe()


if __name__ == "__main__":
    subtitle_folder = Path("/root/datasets/masc/")
    for subset in subtitle_folder.glob("*"):
        if not subset.is_dir():
            logging.warning(f"{subset} is not a directory")
            continue
        logging.info(f"processing {subset.name}...")
        dataframe_path = Path(f"{subset.name}.parquet")
        subset_folder = subset / "subtitles"
        df = vtt_split_to_dataframe(subset_folder, dataframe_path)
        logging.info(f"validating {subset.name}...")
        print(validate_dataframe(df, min_duration=6.0, max_duration=16.0))
