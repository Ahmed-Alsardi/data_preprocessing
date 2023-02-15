from pathlib import Path
from tqdm import tqdm
import logging
import pandas as pd
from processing.config import Audio, SourceEnum
from processing.services import folder_vtt_split, clean_text, split_audio_to_segments


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
    return df


def validate_dataframe(
    df: pd.DataFrame,
    dataframe_path: Path,
    min_duration: float = 6.0,
    max_duration: float = 16.0,
    remove_duplication: bool = True,
) -> pd.Series:
    """
    validate dataframe segments duration
    ensure that the duration between min_duration and max_duration
    Args:
        df: dataframe
        dataframe_path: path to dataframe
        min_duration: minimum duration
        max_duration: maximum duration
        remove_duplication: remove duplication
    Returns:
        Series describing the segment duration
    """
    if df.segment_duration.min() < min_duration:
        raise ValueError(f"min duration is {df.segment_duration.min()}")
    if df.segment_duration.max() > max_duration:
        raise ValueError(f"max duration is {df.segment_duration.max()}")
    if dataframe_path.is_dir():
        raise ValueError("dataframe_path should be a path to a file.")
    if dataframe_path.suffix != ".parquet":
        raise ValueError("dataframe_path should be a parquet file.")
    if remove_duplication:
        df = df.drop_duplicates()
    logging.info("Saving dataframe to parquet file.")
    df.to_parquet(dataframe_path)
    return df


def split_subset_to_audio(
    df: pd.DataFrame,
    subset_audio_folder: Path,
    subset_output_folder: Path,
    audio_extension: str = "wav",
) -> None:
    """
    split audio files into segments, grouped by audio_filename
    Args:
        df: dataframe
        subset_audio_folder: path to audio files
        subset_output_folder: path to output folder
    """
    df = df.groupby("audio_filename")
    total_audios = len(df)
    logging.info(f"total audios: {total_audios}")
    for audio_name, audio_segments in tqdm(df, total=total_audios):
        audio_path = subset_audio_folder / f"{audio_name}.{audio_extension}"
        if not audio_path.is_file():
            logging.warning(f"{audio_path} is not a file")
            continue
        split_audio_to_segments(
            audio=audio_path,
            audio_segments=audio_segments,
            output_dir=subset_output_folder,
            extension=audio_extension,
        )


def masc_subtitle_to_dataframe():
    masc_folder = Path("/root/datasets/masc/")
    for subset in masc_folder.glob("*"):
        if not subset.is_dir():
            logging.warning(f"{subset} is not a directory")
            continue
        logging.info(f"processing {subset.name}...")
        dataframe_path = Path(f"{subset.name}.parquet")
        subset_folder = subset / "subtitles"
        df = vtt_split_to_dataframe(subset_folder)
        logging.info(f"validating {subset.name}...")
        df = validate_dataframe(
            df=df, dataframe_path=dataframe_path, min_duration=6.0, max_duration=16.0
        )
        logging.info(df.segment_duration.describe())


def masc_dataframe_to_audio():
    masc_folder = Path("/root/datasets/masc/")
    for subset in masc_folder.glob("*"):
        if not subset.is_dir():
            logging.warning(f"{subset} is not a directory")
            continue
        logging.info(f"processing {subset.name}...")
        dataframe = pd.read_parquet(f"{subset.name}.parquet")
        subset_folder = subset / "audios"
        subset_output = subset / "segments"
        subset_output.mkdir(exist_ok=True)
        split_subset_to_audio(dataframe, subset_folder, subset_output)


if __name__ == "__main__":
    # masc_subtitle_to_dataframe()
    masc_dataframe_to_audio()
