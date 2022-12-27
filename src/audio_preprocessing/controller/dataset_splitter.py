import os
import asyncio
from pathlib import Path
import logging
from dotenv import load_dotenv
from audio_preprocessing.services import splitting_vtt
from audio_preprocessing.db import models, audio_db
from audio_preprocessing.s3_data_provider import S3SubtitleProvider, S3Config

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# S3 configuration
AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
AWS_SUBTITLE_PREFIX = 'masc/clean_train/subtitles'
SUBTITLE_DOWNLOAD_PATH = Path.cwd().parent / "data" / 'subtitles'
AWS_BUCKET_NAME = "arabic-speech-data"

# DB configuration
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
DB_NAME = "testing_integration1"


def get_s3_provider() -> S3SubtitleProvider:
    s3_config = S3Config(
        access_key=AWS_ACCESS_KEY,
        secret_key=AWS_SECRET_KEY,
        subtitle_prefix=AWS_SUBTITLE_PREFIX,
        bucket_name=AWS_BUCKET_NAME
    )
    return S3SubtitleProvider(s3_config=s3_config, subtitle_download_path=SUBTITLE_DOWNLOAD_PATH)


async def initialize_db():
    db_config = audio_db.DBConfig(
        username=MONGODB_USERNAME,
        password=MONGODB_PASSWORD,
        db_name=DB_NAME
    )
    await audio_db.connect_to_mongo(db_config=db_config, document_models=models.DOCUMENT_LIST)


async def main():
    s3_provider: S3SubtitleProvider = get_s3_provider()
    logging.info("Connected to S3 Provider")
    logging.info("Trying to connect to db")
    await initialize_db()
    logging.info("Connected to db")
    for i, audio in enumerate(splitting_vtt.splitter_generator(s3_provider.download_subtitles, step=3)):
        if i == 10:
            break
        await audio_db.save_audio(audio)
        logging.info(f"Audio {audio.audio_id} was saved in db")


if __name__ == '__main__':
    asyncio.run(main())
