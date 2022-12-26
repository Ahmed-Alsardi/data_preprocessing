from typing import Generator, Callable

import pytest
from pathlib import Path
from audio_preprocessing.controller.splitting_vtt import (split_vtt,
                                                          AudioSegment,
                                                          splitter_generator,
                                                          Audio)


@pytest.fixture
def vtt_path() -> Path:
    return Path.cwd() / "test_data" / "test.ar.vtt"


@pytest.fixture
def path_generator() -> Generator[Path, None, None]:
    """
    A generator that yields a path to a vtt file
    :return:
    """
    root_path = Path.cwd() / "test_data"
    yield lambda: root_path.glob("*.vtt")


audio_sub_segments = [
    (10, [
        AudioSegment(start=15_740, end=46_340,
                     text=" ".join([str(i + 1) for i in range(10)])),
        AudioSegment(start=46_340, end=75_860,
                     text=" ".join([str(i + 1) for i in range(10, 20)]))
    ]),
    (5, [
        AudioSegment(start=15_740, end=34_640,
                     text=" ".join([str(i + 1) for i in range(5)])),
        AudioSegment(start=34_640, end=46_340,
                     text=" ".join([str(i + 1) for i in range(5, 10)])),
        AudioSegment(start=46_340, end=60_240,
                     text=" ".join([str(i + 1) for i in range(10, 15)])),
        AudioSegment(start=60_240, end=75_860,
                     text=" ".join([str(i + 1) for i in range(15, 20)])),
    ]),
    (8, [
        AudioSegment(start=15_740, end=41_760,
                     text=" ".join([str(i + 1) for i in range(8)])),
        AudioSegment(start=41_780, end=61_220,
                     text=" ".join([str(i + 1) for i in range(8, 16)])),
        AudioSegment(start=61_220, end=75_860,
                     text=" ".join([str(i + 1) for i in range(16, 20)])),
    ])
]

audio_segments = [(step, segments) for step, segments in audio_sub_segments]


@pytest.mark.parametrize("step, segments", audio_sub_segments)
def test_first_split_vtt(vtt_path, step, segments):
    assert vtt_path.exists(), "vtt file does not exist"
    vtt_segments = split_vtt(vtt_path, step=step)
    assert len(vtt_segments) == len(segments), "number of segments is not correct"
    for actual_segment, expected_segment in zip(vtt_segments, segments):
        assert actual_segment == expected_segment


@pytest.mark.parametrize("step, segments", audio_segments)
def test_splitter_generator(path_generator: Callable[[], Generator[Path, None, None]],
                            step: int, segments: list[AudioSegment]):
    for audio_segment in splitter_generator(path_generator, step=step):
        assert audio_segment.audio_id == "test", "audio id is not correct"
        assert len(audio_segment.audio_segments) == len(segments), "number of segments is not correct"
        assert audio_segment.audio_segments == segments, "segments are not correct"
