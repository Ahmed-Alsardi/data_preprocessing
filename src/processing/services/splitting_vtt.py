import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Generator, Callable, Optional
import webvtt
from processing.db.models import AudioSegment

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


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
        text = " ".join([caption.text for caption in vtt[i : i + step]])
        segments.append(AudioSegment(start=start, end=end, text=text))
    return segments


def get_file_duration(vtt: webvtt.WebVTT) -> float:
    """
    Get the duration of the file from the vtt file.
    :param vtt: webvtt file.
    :return: Callable that returns the duration of the file.
    """
    return sum(
        [
            int((caption.end_in_seconds - caption.start_in_seconds) * 1000)
            for caption in vtt
        ]
    )


def _reset_variables(caption: webvtt.Caption) -> tuple[str, int, int, int]:
    """
    Reset the variables.
    :param caption: webvtt caption
    :return: tuple of text, start, end
    """
    text = caption.text
    start = int(caption.start_in_seconds * 1000)
    end = int(caption.end_in_seconds * 1000)
    duration = int((caption.end_in_seconds - caption.start_in_seconds) * 1000)
    return text, start, end, duration


def v2_split_vtt(
    vtt_path: Path,
    max_length: int = 25_000,
    min_length: int = 15_000,
    threshold: int = 2_500,
) -> list[AudioSegment]:
    """
    Split the vtt file into list of AudioSegment between min_length and max_length.
    """
    segments: list[AudioSegment] = []
    vtt = webvtt.read(vtt_path)
    text = ""
    start = 0
    end = 0
    duration = 0
    file_duration = get_file_duration(vtt)
    print(f"get_file_duration: {file_duration}")
    for caption in vtt:
        caption_length = int((caption.end_in_seconds - caption.start_in_seconds) * 1000)
        if duration + caption_length < max_length:
            # check the threshold before adding the caption
            # if there is big silence between the captions
            # check if the duration is bigger than the min_length
            # if it is, add the segment to the list and reset the variables
            # if not, disacrd the current segment and reset the variables
            if end + threshold > int(caption.start_in_seconds * 1000):
                text += " " + caption.text
                duration += caption_length
                end = int(caption.end_in_seconds * 1000)
            elif duration > min_length:
                segments.append(AudioSegment(start=start, end=end, text=text))
                text, start, end, duration = _reset_variables(caption)
            else:
                text, start, end, duration = _reset_variables(caption)
        else:
            segments.append(AudioSegment(start=start, end=end, text=text))
            text, start, end, duration = _reset_variables(caption)

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
    subtitles_generator: Callable[[], Generator[Path, None, None]], step: int = 4
) -> Generator[Audio, None, None]:
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
        except Exception as splitter_exception:
            logging.error("Error with filename: %s", subtitle_name)
            logging.error(splitter_exception)
            continue
        yield Audio(
            audio_id=subtitle_name,
            audio_segments=audio_segments,
            audio_length=audio_length,
        )


if __name__ == "__main__":
    file_path = Path.cwd().parent / "data" / "subtitles"
    print(file_path.exists())
    if file_path.exists():
        for file in file_path.glob("*"):
            print(file)
            segments = v2_split_vtt(file)
            total = 0
            for i, segment in enumerate(segments):
                print(f"segment {i} duration: {segment.end - segment.start}")
                total += segment.end - segment.start
            print(f"total: {total}")
            print("=" * 30)
    else:
        print("File not found")
        print(Path.cwd())
