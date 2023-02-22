from multiprocessing import Pool, cpu_count
from pathlib import Path
import logging
from typing import Tuple
import pandas as pd
from tqdm import tqdm
import numpy as np
from pydub import AudioSegment


logging.basicConfig(
    filename="error.log",
    filemode="w",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


def _process_audio(data: Tuple[Path, float]):
    audio_path, duration = data
    audio = AudioSegment.from_wav(audio_path)
    if not np.isclose(audio.duration_seconds, duration, atol=1):
        logging.error(
            f"{audio_path} has a duration of {audio.duration_seconds} while the csv says {duration}"
        )
        return audio_path
        # with open("error.txt", "a") as f:
        #     f.write(
        #         f"{audio_path} has a duration of {audio.duration_seconds} while the csv says {duration}"
        #     )


def main(df_path: Path):
    df = pd.read_parquet(df_path)
    df["audio_path"] = df.segment_filename.apply(
        lambda x: Path(f"../data/{df_path.stem}/audio_segments") / f"{x}.wav"
    )
    inputs = list(zip(df.audio_path.values, df.segment_duration.values))
    total = 0
    logging.info("Starting finding errors, length of inputs: %s", len(inputs))
    with Pool(cpu_count()) as p:
        for path in tqdm(p.imap(_process_audio, inputs), total=len(inputs)):
            if path is None:
                continue
            filename = Path(path).stem
            df = df.drop(df[df.segment_filename == filename].index)
            total += 1
    df = df.drop(columns=["audio_path"], axis=1)
    df.to_parquet(f"../data/{df_path.stem}/{df_path.stem}.parquet")
    logging.info("Finished finding errors, total: %s", total)


if __name__ == "__main__":
    train_df = Path("../data/train/train.parquet")
    dev_df = Path("../data/dev/dev.parquet")
    test_df = Path("../data/test/test.parquet")
    logging.info("Starting validating audio train set")
    main(train_df)
    logging.info("Starting validating audio dev set")
    main(dev_df)
    logging.info("Starting validating audio test set")
    main(test_df)
