from pathlib import Path
import logging
import pandas as pd
from processing.config import SourceEnum
from processing.services import clean_text


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


MIN_DURATION = 6.0
MAX_DURATION = 16.0
ENVIRONMENT = "Clean -- نظيف"


def read_sada_csv(csv_path: Path, do_clean_text: bool = True) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    min_filter = df.SegmentLength >= MIN_DURATION
    max_filter = df.SegmentLength <= MAX_DURATION
    df = df[min_filter & max_filter]
    df = df[df.Environment == ENVIRONMENT]
    df = df[df.ProcessedText.notna()]
    df = df.reset_index()
    if do_clean_text:
        df.ProcessedText = df.ProcessedText.apply(clean_text)
    return df


def create_segment_filename(
    df: pd.DataFrame, source: SourceEnum = SourceEnum.SADA
) -> pd.DataFrame:
    df["FileName"] = df.FileName.apply(lambda x: Path(x).stem)
    df["segment_filename"] = df.apply(lambda row: f"{row.FileName}_{row.name}", axis=1)
    df["source"] = source.value
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(
        columns={
            "ProcessedText": "segment_text",
            "SegmentLength": "segment_duration",
            "FileName": "audio_filename",
            "SegmentStart": "segment_start",
            "SegmentEnd": "segment_end",
        }
    )
    return df[
        [
            "audio_filename",
            "segment_filename",
            "segment_start",
            "segment_end",
            "segment_duration",
            "segment_text",
            "source",
        ]
    ]

def validate_datarame(df: pd.DataFrame) -> None:
    assert df.segment_text.notna().all()
    assert df.segment_duration.notna().all()
    assert df.segment_start.notna().all()
    assert df.segment_end.notna().all()
    assert df.segment_filename.notna().all()
    assert df.audio_filename.notna().all()
    assert df.segment_duration.min() >= MIN_DURATION
    assert df.segment_duration.max() <= MAX_DURATION

def process_sada_csv(
    csv_path: Path, source: SourceEnum = SourceEnum.SADA
) -> pd.DataFrame:
    df = read_sada_csv(csv_path)
    df = create_segment_filename(df, source)
    df = rename_columns(df)
    validate_datarame(df)
    df.to_parquet(f"{csv_path.stem}.parquet")
    return df


if __name__ == "__main__":
    train_path = Path("/root/datasets/sada/train.csv")
    dev_path = Path("/root/datasets/sada/dev.csv")
    test_path = Path("/root/datasets/sada/test.csv")
    logger.info("process train data")
    train_df = process_sada_csv(train_path)
    logger.info("process dev data")
    dev_df = process_sada_csv(dev_path)
    logger.info("process test data")
    test_df = process_sada_csv(test_path)
    logger.info(f"train: {len(train_df)}, dev: {len(dev_df)}, test: {len(test_df)}")
