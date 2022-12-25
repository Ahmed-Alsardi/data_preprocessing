import pytest
from pathlib import Path
from audio_preprocessing.controller.splitting_vtt import split_vtt, AudioSegment


@pytest.fixture
def vtt_path() -> Path:
    return Path.cwd() / "test_data" / "test.ar.vtt"


audio_segments = [
    (10, [
        AudioSegment(start=15_740, end=46_340,
                     text=" ".join([str(i + 1) for i in range(10)])),
        AudioSegment(start=46_340, end=75_860,
                     text=" ".join([str(i + 1) for i in range(10, 20)]))]),
    (5, [
        AudioSegment(start=15_740, end=34_640,
                     text=" ".join([str(i + 1) for i in range(5)])),
        AudioSegment(start=34_640, end=46_340,
                     text=" ".join([str(i + 1) for i in range(5, 10)])),
        AudioSegment(start=46_340, end=60_240,
                     text=" ".join([str(i + 1) for i in range(10, 15)])),
        AudioSegment(start=60_240, end=75_860,
                     text=" ".join([str(i + 1) for i in range(15, 20)])),
    ])
]


@pytest.mark.parametrize("step, segments", audio_segments)
def test_first_split_vtt(vtt_path, step, segments):
    assert vtt_path.exists(), "vtt file does not exist"
    vtt_segments = split_vtt(vtt_path, step=step)
    assert len(vtt_segments) == len(segments), "number of segments is not correct"
    for actual_segment, expected_segment in zip(vtt_segments, segments):
        assert actual_segment == expected_segment
