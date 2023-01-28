import pytest
from processing.sada.services.split_audio import (
    combine_df_rows,
    AudioFile,
    AudioSegment,
)
import pandas as pd


@pytest.fixture
def df():
    data = {
        "FileName": ["file1.wav", "file2.wav", "file3.wav", "file4.wav", "file4.wav"],
        "SegmentStart": [0, 0, 0, 0, 0],
        "SegmentEnd": [12.5, 15.5, 7, 17, 10],
        "ProcessedText": ["hello", "world", "this", "is", "a test"],
    }
    return pd.DataFrame(data)



def test_combine_df_rows_with_correct_expected(df):
    expected = [
        AudioFile(
            filename="file1.wav",
            duration=28,
            segments=[
                AudioSegment(filename="file1.wav", start=0, end=12.5, text="hello"),
                AudioSegment(filename="file2.wav", start=0, end=15.5, text="world"),
            ],
        ),
        AudioFile(
            filename="file2.wav",
            duration=24,
            segments=[
                AudioSegment(filename="file3.wav", start=0, end=7, text="this"),
                AudioSegment(filename="file4.wav", start=0, end=17, text="is"),
            ],
        ),
    ]
    assert len(expected) == len(list(combine_df_rows(df))), "Length is not equal"
    for expected, actual in zip(expected, combine_df_rows(df)):
        assert expected.duration == actual.duration
        assert expected.segments == actual.segments


def test_combine_df_rows_with_wrong_duration(df):
    expected = [
        AudioFile(
            filename="file1.wav",
            duration=2,
            segments=[
                AudioSegment(filename="file1.wav", start=0, end=12.5, text="hello"),
                AudioSegment(filename="file2.wav", start=0, end=15.5, text="world"),
            ],
        ),
        AudioFile(
            filename="file2.wav",
            duration=2,
            segments=[
                AudioSegment(filename="file3.wav", start=0, end=7, text="this"),
                AudioSegment(filename="file4.wav", start=0, end=17, text="is"),
            ],
        ),
    ]
    assert len(expected) == len(list(combine_df_rows(df))), "Length is not equal"
    for expected, actual in zip(expected, combine_df_rows(df)):
        assert expected.duration != actual.duration, "Duration should not be equal"
        assert expected.segments == actual.segments, "Segments are not equal"
    

def test_combine_df_rows_with_wrong_segments(df):
    expected = [
        AudioFile(
            filename="file1.wav",
            duration=28,
            segments=[
                AudioSegment(filename="file1.wav", start=0, end=12.5, text="hello"),
            ],
        ),
        AudioFile(
            filename="file2.wav",
            duration=24,
            segments=[
                AudioSegment(filename="file3.wav", start=0, end=7, text="this"),
                AudioSegment(filename="file4.wav", start=0, end=17, text="is"),
                AudioSegment(filename="file4.wav", start=0, end=17, text="is"),
            ],
        ),
    ]
    assert len(expected) == len(list(combine_df_rows(df))), "Length is not equal"
    for expected, actual in zip(expected, combine_df_rows(df)):
        assert expected.duration == actual.duration, "Duration should be equal"
        assert expected.segments != actual.segments, "Segments should not be equal"

def test_combine_df_rows_with_wrong_length(df):
    expected = [
        AudioFile(
            filename="file1.wav",
            duration=28,
            segments=[
                AudioSegment(filename="file1.wav", start=0, end=12.5, text="hello"),
                AudioSegment(filename="file2.wav", start=0, end=15.5, text="world"),
            ],
        ),
        AudioFile(
            filename="file2.wav",
            duration=24,
            segments=[
                AudioSegment(filename="file3.wav", start=0, end=7, text="this"),
                AudioSegment(filename="file4.wav", start=0, end=17, text="is"),
            ],
        ),
        AudioFile(
            filename="file2.wav",
            duration=24,
            segments=[
                AudioSegment(filename="file3.wav", start=0, end=7, text="this"),
                AudioSegment(filename="file4.wav", start=0, end=17, text="is"),
            ],
        ),
    ]
    assert len(expected) != len(list(combine_df_rows(df))), "Length should not be equal"
