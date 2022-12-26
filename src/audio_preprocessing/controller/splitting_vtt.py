from pathlib import Path
import webvtt
from dataclasses import dataclass


@dataclass
class AudioSubSegment:
    """
    Class to represent an audio segment.
    start and end are in milliseconds.
    """
    start: int
    end: int
    text: str


def split_vtt(vtt_path: Path, step: int = 3) -> list[AudioSegment]:
    """
    Split a vtt file into list of AudioSegment.
    :param vtt_path: Path to the vtt file.
    :param step: caption step
    :return: list of AudioSegment
    """
    vtt = webvtt.read(vtt_path)
    segments: list[AudioSubSegment] = []
    for i in range(0, len(vtt), step):
        start = int(vtt[i].start_in_seconds * 1000)
        if i + step > len(vtt):
            difference = i + step - len(vtt)
            end = int(vtt[i + difference - 1].end_in_seconds * 1000)
        else:
            end = int(vtt[i + step - 1].end_in_seconds * 1000)
        text = " ".join([caption.text for caption in vtt[i:i + step]])
        segments.append(AudioSubSegment(start, end, text))
    return segments


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
