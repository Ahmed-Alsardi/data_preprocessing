import pytest
from pathlib import Path
from audio_preprocessing.controller.splitting_vtt import split_vtt


@pytest.fixture
def vtt_path() -> Path:
    return Path.cwd() / "test_data" / "test.ar.vtt"


@pytest.mark.parametrize("step, length, start, end, text", [
    (10, 2, 15_740, 46_340, " ".join([str(i + 1) for i in range(10)])),
    (5, 4, 15_740, 34_640, " ".join([str(i + 1) for i in range(5)])),
])
def test_first_split_vtt(vtt_path, step, length, start, end, text):
    assert vtt_path.exists(), "vtt file does not exist"
    audio_segments = split_vtt(vtt_path, step=step)
    assert len(audio_segments) == length, "wrong number of audio segments"
    assert audio_segments[0].start == start, "wrong start time"
    assert audio_segments[0].end == end, "wrong end time"
    assert audio_segments[0].text == text, "wrong text"


@pytest.mark.parametrize("step, length, start, end, text", [
    (10, 2, 46_340, 75_860, " ".join([str(i + 1) for i in range(10, 20)])),
    (5, 4, 34_640, 46_340, " ".join([str(i + 1) for i in range(5, 10)])),
])
def test_second_split_vtt(vtt_path, step, length, start, end, text):
    assert vtt_path.exists(), "vtt file does not exist"
    audio_segments = split_vtt(vtt_path, step=step)
    assert len(audio_segments) == length, "wrong number of audio segments"
    assert audio_segments[1].start == start, "wrong start time"
    assert audio_segments[1].end == end, "wrong end time"
    assert audio_segments[1].text == text, "wrong text"
