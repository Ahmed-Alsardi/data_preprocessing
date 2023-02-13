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
    start = vtt[0].start_in_seconds
    end = vtt[0].end_in_seconds
    duration = end - start
    text = vtt[0].text
    for caption in vtt[1:]:
        caption_duration = caption.end_in_seconds - caption.start_in_seconds
        if caption.start_in_seconds - end > threshold:
            # difference between current caption and previous caption is greater than threshold
            if duration >= min_duration:
                segments.append(
                    AudioSegment(
                        start=start,
                        end=end,
                        text=text,
                        source=source,
                        filename=f"{filename}_{len(segments)}",
                    )
                )
            start, end, duration, text = (
                caption.start_in_seconds,
                caption.end_in_seconds,
                caption_duration,
                caption.text,
            )
        if duration + caption_duration <= max_duration:
            # current caption can be added to the segment
            end, duration, text = (
                caption.end_in_seconds,
                duration + caption_duration,
                f"{text} {caption.text}",
            )
        else:
            # current caption cannot be added to the segment
            segments.append(
                AudioSegment(
                    start=start,
                    end=end,
                    text=text,
                    source=source,
                    filename=f"{filename}_{len(segments)}",
                )
            )
            start, end, duration, text = (
                caption.start_in_seconds,
                caption.end_in_seconds,
                caption_duration,
                caption.text,
            )
    if duration >= min_duration:
        segments.append(
            AudioSegment(
                start=start,
                end=end,
                text=text,
                source=source,
                filename=f"{filename}_{len(segments)}",
            )
        )
    audio = Audio(
        filename=filename,
        duration=sum([segment.duration for segment in segments]),
        segments=segments,
        source=source,
    )
    return audio
