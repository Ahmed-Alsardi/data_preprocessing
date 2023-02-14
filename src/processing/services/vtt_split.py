from pathlib import Path
import webvtt
from tqdm import tqdm
from processing.config import Audio, AudioSegment, SourceEnum


def vtt_split(
    vtt_path: Path,
    min_duration: float = 6.0,
    max_duration: float = 16.0,
    threshold: float = 2.0,
    source: SourceEnum = SourceEnum.MASC,
) -> Audio:
    """
    Split a vtt file into audio segments

    Args:
        vtt_path: path to vtt file
        min_duration: minimum duration of a segment
        max_duration: maximum duration of a segment
        threshold: threshold for splitting segments
        source: source of the audio
    Returns:
        Audio object
    """
    vtt = webvtt.read(vtt_path)
    filename = vtt_path.stem
    segments = []
    current_segment = AudioSegment(
        start=vtt[0].start_in_seconds,
        end=vtt[0].end_in_seconds,
        text=vtt[0].text,
        source=source,
        filename=f"{filename}_{len(segments)}",
    )
    for caption in vtt[1:]:
        caption_duration = caption.end_in_seconds - caption.start_in_seconds
        if caption.start_in_seconds - current_segment.end > threshold:
            # difference between current caption and previous caption is greater than threshold
            if current_segment.duration >= min_duration:
                segments.append(current_segment)
            current_segment = AudioSegment(
                start=caption.start_in_seconds,
                end=caption.end_in_seconds,
                text=caption.text,
                source=source,
                filename=f"{filename}_{len(segments)}",
            )
            continue
        if current_segment.duration + caption_duration <= max_duration:
            # current caption can be added to the segment
            current_segment.end = caption.end_in_seconds
            current_segment.text = f"{current_segment.text} {caption.text}"
        elif current_segment.duration >= min_duration:
            # current caption cannot be added to the segment
            segments.append(current_segment)
            current_segment = AudioSegment(
                start=caption.start_in_seconds,
                end=caption.end_in_seconds,
                text=caption.text,
                source=source,
                filename=f"{filename}_{len(segments)}",
            )
        else:
            # current caption cannot be added to the segment bc it's big and current segment is too short
            # skip the current caption and start a new segment
            current_segment = AudioSegment(
                start=caption.start_in_seconds,
                end=caption.end_in_seconds,
                text=caption.text,
                source=source,
                filename=f"{filename}_{len(segments)}",
            )
    if current_segment.duration >= min_duration:
        segments.append(current_segment)
    audio = Audio(
        filename=filename,
        duration=sum([segment.duration for segment in segments]),
        segments=segments,
        source=source,
    )
    return audio


def folder_vtt_split(
    vtt_folder: Path,
    min_duration: float = 6.0,
    max_duration: float = 16.0,
    threshold: float = 2.0,
    source: SourceEnum = SourceEnum.MASC,
) -> list[Audio]:
    """
    Split a folder of vtt files into audio segments

    Args:
        vtt_folder: path to folder of vtt files
        min_duration: minimum duration of a segment
        max_duration: maximum duration of a segment
        threshold: threshold for splitting segments
        source: source of the audio
    Returns:
        list of Audio objects
    """
    audios = []
    for vtt_path in tqdm(
        vtt_folder.glob("*"),
        desc="Splitting vtt files into segments",
        total=len(list(vtt_folder.glob("*"))),
    ):
        if vtt_path.suffix == ".vtt":
            audios.append(
                vtt_split(
                    vtt_path=vtt_path,
                    min_duration=min_duration,
                    max_duration=max_duration,
                    threshold=threshold,
                    source=source,
                )
            )

    return audios


if __name__ == "__main__":
    vtt_path = Path("/root/datasets/masc/train/subtitles/frrRoqxg67k.ar.vtt")
    audio = vtt_split(vtt_path=vtt_path)
