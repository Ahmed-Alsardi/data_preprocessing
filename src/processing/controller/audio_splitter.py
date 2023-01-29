import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from tqdm import tqdm
from processing.db.models import Audio, AudioSegment
from processing.services.audio_split import split_audio
from multiprocessing import Pool
from processing.db.audio_db import MongoDB, AudioCollection, DBConfig
from processing.s3_data_provider.s3_provider import S3AudioProvider, S3Config


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

load_dotenv()

# S3 configuration
TARGET_SET = "clean_train"
ROOT_DOWNLOAD_PATH = Path(f"/mnt/volume_sfo3_01/data/{TARGET_SET}")
AUDIO_DOWNLOAD_PATH = Path("../data") / "audios"
AUDIO_SEGMENT_DOWNLOAD_PATH = ROOT_DOWNLOAD_PATH / "audio_segments"

AWS_BUCKET_NAME = "arabic-speech-data"

# DB configuration
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_NAME = os.getenv("MONGODB_NAME")


def initialize_db() -> MongoDB:
    config = DBConfig(
        username=MONGODB_USERNAME,
        password=MONGODB_PASSWORD,
        db_name=MONGODB_NAME,
        host=MONGODB_HOST,
    )
    return MongoDB(config)


def add_audio_to_csv(csv_file: Path, audio_segment: AudioSegment):
    """
    Add audio segment to csv file, create csv file if not exists.
    Args:
        csv_file: csv file path
        audio_segment: audio segment to add to csv file
    """
    if not csv_file.exists():
        with open(csv_file, "w") as f:
            f.write("filename,text,duration\n")
    with open(csv_file, "a") as f:
        f.write(
            f"{audio_segment.filename},{audio_segment.text},{audio_segment.duration}\n"
        )


def process_audio(audio: Audio):
    audio_path = AUDIO_DOWNLOAD_PATH / f"{audio.audio_id}.wav"
    for segment in split_audio(
        audio_path=audio_path,
        audio_meta=audio,
        output_dir=AUDIO_SEGMENT_DOWNLOAD_PATH,
    ):
        # save audio in csv file
        add_audio_to_csv(
            csv_file=ROOT_DOWNLOAD_PATH / "clean_train.csv", audio_segment=segment
        )


def main():
    logging.info("Trying to connect to db.")
    audio_db = initialize_db()
    audio_collection = audio_db.get_collection(TARGET_SET)
    all_audios = audio_collection.find_all()
    # run multi-threaded for prcoessing audio
    # process_audio(all_audios)
    with Pool(3) as pool:
        list(tqdm(pool.imap(process_audio, all_audios), total=len(all_audios)))


if __name__ == "__main__":
    main()
