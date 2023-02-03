from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from pprint import pprint
from typing import Generator, Tuple, Optional
import secrets
import pandas as pd
from pydub import AudioSegment as PydubAudioSegment


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


class Environment(Enum):
    CLEAN = "Clean -- نظيف"
    NOISE = "Noise -- ضوضاء"
    MUSIC = "Music -- موسيقى"
    CAR = "Car -- سيارة"



ROOT_PATH = Path("~/dev/sada/").expanduser()
OUTPUT_DIR = Path("../data")


def combine_df_rows(
    df: pd.DataFrame, min_length=30
) -> Generator[AudioFile, None, None]:
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
    for i, row in df.iterrows():
        audio_filename = f"{secrets.token_urlsafe(5)}_{i}.wav"
        filename = row["FileName"]
        start = row["SegmentStart"]
        end = row["SegmentEnd"]
        text = row["ProcessedText"]
        if not isinstance(text, str):
            print(f"Text is not a string: {text}")
            continue
        duration += end - start
        segments.append(AudioSegment(filename, start, end, text))
        if duration >= min_length:
            yield AudioFile(audio_filename, duration, segments)
            duration = 0
            segments = []


def combine_audio_file(
    audio_path: Path,
    audio_meta: AudioFile,
    output_dir: Path,
    silence_duration: float = 30,
) -> True:
    """
    Combine several audio files into one audio file.
    Args:
        audio_path: Path to the audio files
        audio: AudioFile object
        output_dir: Path to the output directory
        silence_duration: duration of the silence between the audio files
    Returns:
        True if the audio file is successfully created, False otherwise.
    """
    try:
        audio = PydubAudioSegment.empty()
        for segment in audio_meta.segments:
            audio += PydubAudioSegment.from_wav(audio_path / segment.filename)[
                int(segment.start * 1000) : int(segment.end * 1000)
            ]
            audio += PydubAudioSegment.silent(duration=silence_duration)
        audio.export(output_dir / audio_meta.filename, format="wav")
        return True
    except Exception as e:
        print(e)
        return False


def add_to_csv_file(csv_path: Path, audio_meta: AudioFile) -> None:
    """
    Add the audio file to a csv file, if the file isn't exists, create a new one.
    Args:
        csv_path: Path to the csv file
        audio_meta: AudioFile object
    """
    if not csv_path.exists():
        with open(csv_path, "w") as f:
            f.write("filename,text,duration\n")
    try:
        with open(csv_path, "a") as f:
            text = " ".join([segment.text for segment in audio_meta.segments])
            f.write(f"{audio_meta.filename},{text},{audio_meta.duration}\n")
    except Exception as e:
        print(e)

def get_dataframe(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    def create_segment_category(segment_length: float) -> str:
        category = [5, 10, 15, 20, 25, 30, 35]
        for i, c in enumerate(category):
            if segment_length <= c:
                return f"less_than_{c}"
        return f"more_than_{category[-1]}"
    df["segment_category"] = df.SegmentLength.apply(create_segment_category)
    return df

def get_environment_df(df: pd.DataFrame, environment: Environment) -> pd.DataFrame:
    print(environment)
    return df[df.Environment == environment.value]

def get_category_df(df: pd.DataFrame, category: str) -> pd.DataFrame:
    return df[df.segment_category == category]


if __name__ == "__main__":
    df = get_dataframe(ROOT_PATH / "train.csv")
    df = get_environment_df(df, Environment.CLEAN)
    df = get_category_df(df, "less_than_5")
    print(df.SegmentLength.sum() / 3600)
    for i, audio_meta in enumerate(combine_df_rows(df)):
        combine_audio_file(ROOT_PATH, audio_meta, OUTPUT_DIR / "audios")
        add_to_csv_file(OUTPUT_DIR / "data.csv", audio_meta)
        print(i)
        if i == 10:
            break
    print("Done")
