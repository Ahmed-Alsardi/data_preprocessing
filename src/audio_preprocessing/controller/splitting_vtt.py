from pathlib import Path
import webvtt
from dataclasses import dataclass
from typing import Generator, Callable


@dataclass
class AudioSegment:
    """
    Class to represent an audio segment.
    start and end are in milliseconds.
    """
    start: int
    end: int
    text: str


@dataclass
class Audio:
    audio_id: str
    audio_segments: list[AudioSegment]


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
            difference = i + step - len(vtt)
            end = int(vtt[i + difference - 1].end_in_seconds * 1000)
        else:
            end = int(vtt[i + step - 1].end_in_seconds * 1000)
        text = " ".join([caption.text for caption in vtt[i:i + step]])
        segments.append(AudioSegment(start, end, text))
    return segments


def splitter_generator(
        subtitles_generator: Callable[[], Generator[Path, None, None]],
        step: int = 4) -> Generator[Audio, None, None]:
    """
    Loop through subtitles and extract the splitting
    :param step: caption step
    :param subtitles_generator: S3SubtitleProvider generate audio subtitle
    :return: a generator of AudioSegments
    """
    for subtitle_path in subtitles_generator():
        subtitle_name = subtitle_path.parts[-1].split(".")[0]
        audio_segments = split_vtt(vtt_path=subtitle_path, step=step)
        yield Audio(audio_id=subtitle_name, audio_segments=audio_segments)


if __name__ == '__main__':
    # file_path = Path.cwd().parent / "S3DataProvider" / "subtitles" / "-2vjWSEQF-Q.ar.vtt"
    file_path = Path.cwd().parent.parent.parent / "tests" / "controller" / "test_data" / "test.ar.vtt"
    print(file_path.exists())
    if file_path.exists():
        segments = split_vtt(file_path, 10)
        for segment in segments:
            print(segment)
    else:
        print("File not found")
