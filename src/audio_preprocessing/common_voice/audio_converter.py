from multiprocessing.pool import ThreadPool
from pathlib import Path
import pandas as pd
import tqdm
from pydub import AudioSegment


ROOT_PATH = Path("data/v11/")
AUIDO_PATH = ROOT_PATH / "clips"
TRAIN_TSV_PATH = ROOT_PATH / "train.tsv"
VALID_TSV_PATH = ROOT_PATH / "dev.tsv"
TEST_TSV_PATH = ROOT_PATH / "test.tsv"
TARGET_PATH = ROOT_PATH / "clips_wav"


def convert_audio(audio_path: Path, target_path: Path = TARGET_PATH):
    audio = AudioSegment.from_mp3(audio_path)
    audio_name = audio_path.stem + ".wav"
    audio.export(target_path / audio_name, format="wav")


def convert_dataframe_audio(df: pd.DataFrame):
    audio_paths = [AUIDO_PATH / audio_name for audio_name in df["path"]]
    with ThreadPool(8) as pool:
        for _ in tqdm.tqdm(
            pool.imap_unordered(convert_audio, audio_paths), total=len(audio_paths)
        ):
            pass


def main():
    # train_df = pd.read_csv(TRAIN_TSV_PATH, sep="\t")
    # dev_df = pd.read_csv(VALID_TSV_PATH, sep="\t")
    test_df = pd.read_csv(TEST_TSV_PATH, sep="\t")
    print("=========== Converting test data")
    convert_dataframe_audio(test_df)
    print("=========== Finished converting test data")


if __name__ == "__main__":
    main()
