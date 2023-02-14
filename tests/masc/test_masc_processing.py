import pytest
import pandas as pd
from processing.masc import audio_to_dataframe
from processing.config import Audio, AudioSegment, SourceEnum


def test_audio_to_dataframe_with_single_segment():
    audio = Audio(
        filename="test",
        source=SourceEnum.MASC,
        duration=1.0,
        segments=[
            AudioSegment(
                start=0.0,
                end=1.0,
                text="test",
                source=SourceEnum.MASC,
                filename="test_0",
            )
        ],
    )
    df = audio_to_dataframe([audio])
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 7)
    assert set(df.columns.tolist()) == {
        "audio_filename",
        "segment_filename",
        "segment_start",
        "segment_end",
        "segment_text",
        "segment_duration",
        "source",
    }
    assert df["audio_filename"].tolist() == ["test"]
    assert df["segment_filename"].tolist() == ["test_0"]
    assert df["segment_start"].tolist() == [0.0]
    assert df["segment_end"].tolist() == [1.0]
    assert df["segment_text"].tolist() == ["test"]


def test_audio_to_dataframe_with_multiple_segments():
    audio = Audio(
        filename="test",
        source=SourceEnum.MASC,
        duration=1.0,
        segments=[
            AudioSegment(
                start=0.0,
                end=0.5,
                text="test",
                source=SourceEnum.MASC,
                filename="test_0",
            ),
            AudioSegment(
                start=0.5,
                end=1.0,
                text="test",
                source=SourceEnum.MASC,
                filename="test_1",
            ),
        ],
    )
    df = audio_to_dataframe([audio])
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 7)
    assert set(df.columns.tolist()) == {
        "audio_filename",
        "segment_filename",
        "segment_start",
        "segment_end",
        "segment_text",
        "segment_duration",
        "source",
    }
    assert df["audio_filename"].tolist() == ["test", "test"]
    assert df["segment_filename"].tolist() == ["test_0", "test_1"]
    assert df["segment_start"].tolist() == [0.0, 0.5]
    assert df["segment_end"].tolist() == [0.5, 1.0]
    assert df["segment_text"].tolist() == ["test", "test"]

def test_audio_to_dataframe_with_multiple_audios():
    audio1 = Audio(
        filename="test1",
        source=SourceEnum.MASC,
        duration=1.0,
        segments=[
            AudioSegment(
                start=0.0,
                end=0.5,
                text="test",
                source=SourceEnum.MASC,
                filename="test1_0",
            ),
            AudioSegment(
                start=0.5,
                end=1.0,
                text="test",
                source=SourceEnum.MASC,
                filename="test1_1",
            ),
        ],
    )
    audio2 = Audio(
        filename="test2",
        source=SourceEnum.MASC,
        duration=1.0,
        segments=[
            AudioSegment(
                start=0.0,
                end=0.5,
                text="test",
                source=SourceEnum.MASC,
                filename="test2_0",
            ),
            AudioSegment(
                start=0.5,
                end=1.0,
                text="test",
                source=SourceEnum.MASC,
                filename="test2_1",
            ),
        ],
    )
    df = audio_to_dataframe([audio1, audio2])
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (4, 7)
    assert set(df.columns.tolist()) == {
        "audio_filename",
        "segment_filename",
        "segment_start",
        "segment_end",
        "segment_text",
        "segment_duration",
        "source",
    }
    assert df["audio_filename"].tolist() == ["test1", "test1", "test2", "test2"]
    assert df["segment_filename"].tolist() == ["test1_0", "test1_1", "test2_0", "test2_1"]
    assert df["segment_start"].tolist() == [0.0, 0.5, 0.0, 0.5]
    assert df["segment_end"].tolist() == [0.5, 1.0, 0.5, 1.0]
    assert df["segment_text"].tolist() == ["test", "test", "test", "test"]
