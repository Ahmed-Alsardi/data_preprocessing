from pathlib import Path
import pytest
from processing.services import vtt_split, folder_vtt_split
from processing.config import Audio, AudioSegment, SourceEnum


@pytest.fixture
def vtt_file_without_threshold():
    return (Path("tests") / "test_data" / "test_without_threshold.vtt").absolute()


@pytest.fixture
def vtt_file_with_threshold():
    return (Path("tests") / "test_data" / "test_with_threshold.vtt").absolute()


@pytest.fixture
def vtt_folder():
    return (Path("tests") / "test_data").absolute()


def test_vtt_split_return_without_threshold_segments(vtt_file_without_threshold):
    audio = vtt_split(
        vtt_file_without_threshold,
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
    expected_filename = "test_without_threshold"
    assert audio.filename == expected_filename
    assert len(audio.segments) == len(expected_duration)
    assert audio.duration == sum(expected_duration)
    for i, (segment, duration, text) in enumerate(
        zip(audio.segments, expected_duration, expected_text)
    ):
        assert isinstance(segment, AudioSegment)
        assert segment.duration == duration
        assert segment.source == SourceEnum.MASC
        assert segment.filename == f"{expected_filename}_{i}"
        assert segment.text == text


def test_vtt_split_return_with_threshold_segments(vtt_file_with_threshold):
    audio = vtt_split(
        vtt_file_with_threshold,
        min_duration=8.0,
        max_duration=12.0,
        threshold=2.0,
        source=SourceEnum.MASC,
    )
    expected_duration = [8, 12, 11, 10, 10]
    expected_text = ["1 2", "3 4 5", "7 8 9", "10 11 12", "13 14"]
    assert isinstance(audio, Audio)
    expected_filename = "test_with_threshold"
    assert audio.filename == expected_filename
    assert len(audio.segments) == len(expected_duration)
    assert audio.duration == sum(expected_duration)
    for i, (segment, duration, text) in enumerate(
        zip(audio.segments, expected_duration, expected_text)
    ):
        assert isinstance(segment, AudioSegment)
        assert segment.duration == duration
        assert segment.source == SourceEnum.MASC
        assert segment.filename == f"{expected_filename}_{i}"
        assert segment.text == text


def test_folder_vtt_split(vtt_folder):
    audios = folder_vtt_split(
        vtt_folder, min_duration=8.0, max_duration=12.0, threshold=2.0, source=SourceEnum.MASC
    )
    assert len(audios) == 2, "There should be 2 audios"
    for audio in audios:
        assert isinstance(audio, Audio)
        assert len(audio.segments) > 0, "There should be at least one segment"
        assert audio.duration > 0, "The duration should be greater than 0"
        for segment in audio.segments:
            assert isinstance(segment, AudioSegment)
            assert segment.duration > 0, "The duration should be greater than 0"
            assert segment.source == SourceEnum.MASC
            assert segment.filename is not None, "The filename should not be None"
            assert segment.text is not None, "The text should not be None"
