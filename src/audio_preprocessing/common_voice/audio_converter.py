from multiprocessing.pool import ThreadPool
from pathlib import Path
import logging
import pandas as pd
import tqdm
from pydub import AudioSegment

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


ROOT_PATH = Path("data/v11/")
AUIDO_PATH = ROOT_PATH / "clips"
TRAIN_TSV_PATH = ROOT_PATH / "train.tsv"
DEV_TSV_PATH = ROOT_PATH / "dev.tsv"
TEST_TSV_PATH = ROOT_PATH / "test.tsv"
VALIDATED_TSV_PATH = ROOT_PATH / "validated.tsv"
TARGET_PATH = ROOT_PATH / "clips_wav"


def convert_audio(audio_path: Path, target_path: Path = TARGET_PATH):
    audio = AudioSegment.from_mp3(audio_path)
    audio_name = audio_path.stem + ".wav"
    audio.export(target_path / audio_name, format="wav")


def change_df_audio_path(df: pd.DataFrame):
    df["path"] = df["path"].apply(lambda x: x.replace(".mp3", ".wav"))
    return df


def convert_dataframe_audio(dataframe_path: Path):
    df = pd.read_csv(dataframe_path, sep="\t")
    # check if .wav in df path
    if ".wav" in df["path"].iloc[0]:
        logging.info("Already converted to .wav")
        return
    audio_paths = [AUIDO_PATH / audio_name for audio_name in df["path"]]
    logging.info(
        "Converting %s to .wav, detecting %d files", dataframe_path, len(audio_paths)
    )
    with ThreadPool(8) as pool:
        for _ in tqdm.tqdm(
            pool.imap_unordered(convert_audio, audio_paths), total=len(audio_paths)
        ):
            pass
    change_df_audio_path(df).to_csv(dataframe_path, sep="\t", index=False)
    logging.info("Finished converting %s to .wav", dataframe_path)


def create_target_dir_if_not_exist():
    if not TARGET_PATH.exists():
        TARGET_PATH.mkdir(parents=True, exist_ok=True)


def main():
    logging.info("ROOT_PATH: %s", ROOT_PATH)

    create_target_dir_if_not_exist()
    df_paths = [TRAIN_TSV_PATH, DEV_TSV_PATH, TEST_TSV_PATH, VALIDATED_TSV_PATH]
    for df_path in df_paths:
        convert_dataframe_audio(df_path)


if __name__ == "__main__":
    main()
