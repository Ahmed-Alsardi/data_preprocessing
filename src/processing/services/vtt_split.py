from pathlib import Path
import webvtt
from processing.config import Audio, AudioSegment, SourceEnum


def vtt_split(
    vtt_path: Path,
    min_duration: float = 8.0,
    max_duration: float = 12.0,
    threshold: float = 2.0,
    source: SourceEnum = SourceEnum.MASC,
) -> Audio:
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
        else:
            # current caption cannot be added to the segment
            segments.append(current_segment)
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
