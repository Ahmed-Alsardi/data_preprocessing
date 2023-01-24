import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from tqdm import tqdm
from processing.db.models import Audio, AudioSegment
from processing.services.audio_split import split_audio
from processing.db.audio_db import MongoDB, AudioCollection, DBConfig
from processing.s3_data_provider.s3_provider import S3AudioProvider, S3Config


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

load_dotenv()

# S3 configuration
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
TARGET_SET = "clean_train"
AWS_FOLDER_PREFIX = f"masc/{TARGET_SET}/audios"
ROOT_DOWNLOAD_PATH = Path(f"/mnt/volume_sfo3_01/data/{TARGET_SET}")
AUDIO_DOWNLOAD_PATH = ROOT_DOWNLOAD_PATH / "audios"
AUDIO_SEGMENT_DOWNLOAD_PATH = ROOT_DOWNLOAD_PATH / "audio_segments"

AWS_BUCKET_NAME = "arabic-speech-data"

# DB configuration
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_NAME = os.getenv("MONGODB_NAME")


def get_s3_provider() -> S3AudioProvider:
    s3_config = S3Config(
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        folder_prefix=AWS_FOLDER_PREFIX,
        bucket_name=AWS_BUCKET_NAME,
    )
    return S3AudioProvider(
        s3_config=s3_config,
        audio_download_path=AUDIO_DOWNLOAD_PATH,
    )


def initialize_db() -> MongoDB:
    config = DBConfig(
        username=MONGODB_USERNAME,
        password=MONGODB_PASSWORD,
        db_name=MONGODB_NAME,
        host=MONGODB_HOST,
    )
    return MongoDB(config)


def main():
    logging.info("Trying to connect to AWS.")
    s3_provider: S3AudioProvider = get_s3_provider()
    logging.info("Trying to connect to db.")
    audio_db = initialize_db()
    audio_collection = audio_db.get_collection(TARGET_SET)
    all_audios = audio_collection.find_all()
    for audio in tqdm(all_audios, total=len(all_audios)):
        audio_path = s3_provider.download(f"{audio.audio_id}.wav")
        split_audio(
            audio_path=audio_path,
            audio_meta=audio,
            output_dir=AUDIO_SEGMENT_DOWNLOAD_PATH,
        )
        break


if __name__ == "__main__":
    main()
