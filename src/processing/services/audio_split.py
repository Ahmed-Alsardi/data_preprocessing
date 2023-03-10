from pathlib import Path
from typing import Optional, Tuple, Union
import logging
from pydub import AudioSegment as PydubAudioSegment
import pandas as pd
from processing.config import AudioSegment


logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def _split_audio(
    audio: PydubAudioSegment,
    segment_series: pd.Series,
    output_dir: Path,
    extension: str = "mp3",
) -> int:
    """
    Split an audio file to multiple segments.
    Args:
        audio: audio file path or AudioSegment object, if audio path, audio_dir must be provided.
        segment_series: pandas series with the following columns:
            - segment_filename
            - segment_start
            - segment_end
        output_dir: output directory to save the new audio files.
        extension: audio file extension.
    Returns:
        True if the audio was split successfully, False otherwise.
    """
    start = int(segment_series.segment_start * 1000)
    end = int(segment_series.segment_end * 1000)
    filename = f"{segment_series.segment_filename}.{extension}"
    try:
        seg = audio[start:end]
        seg.export(output_dir / filename, format=extension)
        return 1
    except Exception as e:
        logger.error("%s with filename: %s", e, filename)
        return 0


def split_audio_to_segments(
    audio: Union[Path, PydubAudioSegment],
    audio_segments: pd.DataFrame,
    output_dir: Path,
    extension: str = "mp3",
) -> int:
    total = 0
    if isinstance(audio, Path):
        if not audio.exists():
            logger.error("Audio file %s does not exist.", audio)
            raise FileNotFoundError(f"Audio file {audio} does not exist.")
        audio = PydubAudioSegment.from_wav(audio)
    for _, series_segments in audio_segments.iterrows():
        total += _split_audio(audio, series_segments, output_dir, extension)
    return total
    # total = 0
    # audio_segments, audio_dir, output_dir = data
    # # if isinstance(audio, (str, Path)):
    # audio = audio_dir / f"{audio_segments.audio_filename.values[0]}.{input_extension}"
    # if not audio.exists():
    #     logger.error("Audio file %s does not exist.", audio)
    #     raise FileNotFoundError(f"Audio file {audio} does not exist.")
    # audio = PydubAudioSegment.from_wav(audio)
    # for _, series_segments in audio_segments.iterrows():
    #     print(series_segments)
    #     total += _split_audio(audio, series_segments, output_dir, extension)
    # return total
