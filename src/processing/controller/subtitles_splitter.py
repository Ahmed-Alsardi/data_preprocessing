import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from processing.services import splitting_vtt
from processing.db.audio_db import MongoDB, AudioCollection, DBConfig
from processing.s3_data_provider import S3SubtitleProvider, S3Config
from tqdm import tqdm

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# S3 configuration
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
TARGET_SET = "clean_dev"
AWS_SUBTITLE_PREFIX = f"masc/{TARGET_SET}/subtitles"
SUBTITLE_DOWNLOAD_PATH = Path(f"/mnt/volume_sfo3_01/data/{TARGET_SET}/subtitles")
AWS_BUCKET_NAME = "arabic-speech-data"

# DB configuration
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_NAME = os.getenv("MONGODB_NAME")


def get_s3_provider() -> S3SubtitleProvider:
    s3_config = S3Config(
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        folder_prefix=AWS_SUBTITLE_PREFIX,
        bucket_name=AWS_BUCKET_NAME,
    )
    return S3SubtitleProvider(
        s3_config=s3_config, subtitle_download_path=SUBTITLE_DOWNLOAD_PATH
    )


def initialize_db() -> MongoDB:
    config = DBConfig(
        username=MONGODB_USERNAME,
        password=MONGODB_PASSWORD,
        db_name=MONGODB_NAME,
        host=MONGODB_HOST,
    )
    return MongoDB(config)


def initialize_dirs():
    if not SUBTITLE_DOWNLOAD_PATH.exists():
        SUBTITLE_DOWNLOAD_PATH.mkdir(parents=True)


def main():
    initialize_dirs()
    logging.info("USING %s SET!!!", TARGET_SET)
    s3_provider: S3SubtitleProvider = get_s3_provider()
    logging.info("Connected to S3 Provider")
    logging.info("Trying to connect to db")
    audio_db = initialize_db()
    logging.info("Connected to db. get %s collection.", TARGET_SET)
    audio_collection: AudioCollection = audio_db.get_collection(TARGET_SET)
    for audio in tqdm(
        splitting_vtt.splitter_generator(s3_provider.download_subtitles),
        total=len(s3_provider.subtitle_list),
    ):
        if audio.audio_length == 0:
            continue
        audio_collection.insert_one(audio.dict())
    logging.info("========= Done")


if __name__ == "__main__":
    main()
