import logging
from pathlib import Path
import webvtt
from dataclasses import dataclass
from typing import Generator, Callable
from audio_preprocessing.db.models import AudioSegment

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


@dataclass
class Audio:
    """
    Class to represent an audio. which will be converted to AudioDocument.
    """
    audio_id: str
    audio_segments: list[AudioSegment]
    audio_length: float


def split_vtt(vtt_path: Path, step: int = 3) -> list[AudioSegment]:
    """
    Split a vtt file into list of AudioSegment.
    :param vtt_path: Path to the vtt file.
    :param step: caption step
    :return: list of AudioSegment
    """
    vtt = webvtt.read(vtt_path)
    segments: list[AudioSegment] = []
    for i in range(0, len(vtt), step):
        start = int(vtt[i].start_in_seconds * 1000)
        if i + step > len(vtt):
            difference = step - (i + step - len(vtt))
            end = int(vtt[i + difference - 1].end_in_seconds * 1000)
        else:
            end = int(vtt[i + step - 1].end_in_seconds * 1000)
        text = " ".join([caption.text for caption in vtt[i:i + step]])
        segments.append(AudioSegment(start=start, end=end, text=text))
    return segments


def calculate_audio_length(audio_segments: list[AudioSegment]) -> float:
    """
    Calculate the audio length in seconds.
    :param audio_segments: list of AudioSegment
    :return: length in seconds
    """
    total_length = 0
    for segment in audio_segments:
        total_length += segment.end - segment.start
    return total_length / 1000


def splitter_generator(
        subtitles_generator: Callable[[], Generator[Path, None, None]],
        step: int = 4) -> Generator[Audio, None, None]:
    """
    Loop through subtitles and extract the splitting
    :param step: caption step
    :param subtitles_generator: S3SubtitleProvider generate audio subtitles
    :return: a generator of AudioSegments
    """
    for subtitle_path in subtitles_generator():
        subtitle_name = subtitle_path.parts[-1].split(".")[0]
        try:
            audio_segments = split_vtt(vtt_path=subtitle_path, step=step)
            audio_length = calculate_audio_length(audio_segments)
        except Exception as e:
            logging.error(f"Error with filename: {subtitle_name}")
            logging.error(e)
            continue
        yield Audio(audio_id=subtitle_name, audio_segments=audio_segments, audio_length=audio_length)


if __name__ == '__main__':
    file_path = Path.cwd().parent / "data" / "subtitles" / "-0R1I26YwAE.ar.vtt"
    print(file_path.exists())
    if file_path.exists():
        segments = split_vtt(file_path, 10)
        for segment in segments:
            print(segment)
    else:
        print("File not found")
