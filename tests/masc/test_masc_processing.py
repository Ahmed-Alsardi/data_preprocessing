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
