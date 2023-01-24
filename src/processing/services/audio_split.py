from pathlib import Path
import logging
from pydub import AudioSegment
from processing.db.models import Audio, AudioSegment as AudioSegmentModel

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def split_segment(
    audio: AudioSegment,
    start: int,
    end: int,
    filename: str,
    output_dir: Path,
) -> None:
    """
    Split audio file into two parts.
    start and end are in milliseconds.
    save the new audio file in output_dir.
    """
    seg = audio[start:end]
    seg.export(output_dir / filename, format="mp3")


def split_audio(
    audio_path: Path, audio_meta: Audio, output_dir: Path, extension: str = "mp3"
) -> None:
    """
    Split audio file into multiple audio files.
    save the new audio files in output_dir.
    """
    audio = AudioSegment.from_wav(audio_path / f"{audio_meta.audio_id}.wav")
    for i, segment in enumerate(audio_meta.audio_segments):
        filename = f"{audio_meta.audio_id}_{i}.{extension}"
        split_segment(
            audio=audio,
            start=segment.start,
            end=segment.end,
            filename=filename,
            output_dir=output_dir,
        )


if __name__ == "__main__":
    audio_path = Path("../data/audios")
    output_dir = Path("data/audio_split")
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    audio = Audio(
        audio_id="--lLrhhJ3QA",
        audio_length=50,
        audio_segments=[
            AudioSegmentModel(
                start=0,
                end=10000,
                text="Hello, this is a test audio.",
            ),
            AudioSegmentModel(
                start=10000,
                end=20000,
                text="This is the second segment.",
            ),
            AudioSegmentModel(
                start=20000,
                end=30000,
                text="This is the third segment.",
            ),
        ],
    )
    split_audio(audio_path, audio, output_dir)
