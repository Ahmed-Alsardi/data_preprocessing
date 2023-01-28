from pathlib import Path
from dataclasses import dataclass
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


if __name__ == "__main__":
    df = pd.read_csv(ROOT_PATH / "train.csv")
    for audio_meta in combine_df_rows(df):
        pprint(audio_meta)
        combine_audio_file(ROOT_PATH, audio_meta, OUTPUT_DIR)
        print("Done")
        break