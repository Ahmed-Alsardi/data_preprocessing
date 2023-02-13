from pathlib import Path
import pytest
from processing.services import vtt_split
from processing.config import Audio, AudioSegment, SourceEnum


@pytest.fixture
def vtt_file():
    return (Path("tests") / "test_data" / "test.vtt").absolute()


def test_vtt_split_return_correct_segments(vtt_file):
    audio = vtt_split(
        vtt_file,
        min_duration=8.0,
        max_duration=12.0,
        threshold=2.0,
        source=SourceEnum.MASC,
    )
    expected_duration = [8.0, 11.0, 12.0, 11.0, 10.0, 8.0]
    expected_text = [
        "1 2 3",
        "4 5",
        "6 7 8 9 10",
        "11 12 13 14",
        "15 16 17 18",
        "19 20",
    ]
    assert isinstance(audio, Audio)
    assert audio.filename == "test"
    assert len(audio.segments) == 6
    assert audio.duration == sum(expected_duration)
    for i, (segment, duration, text) in enumerate(
        zip(audio.segments, expected_duration, expected_text)
    ):
        assert isinstance(segment, AudioSegment)
        assert segment.duration == duration
        assert segment.source == SourceEnum.MASC
        assert segment.filename == f"test_{i}"
        assert segment.text == text
