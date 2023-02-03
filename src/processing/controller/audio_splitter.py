import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from tqdm import tqdm
from processing.db.models import Audio, AudioSegment, MASCAudio
from processing.services.audio_split import split_audio
from multiprocessing import Pool, cpu_count
from processing.db.audio_db import MongoDB, AudioCollection, DBConfig
from processing.s3_data_provider.s3_provider import S3AudioProvider, S3Config


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

load_dotenv()


TARGET_SET = "clean_dev"
AUDIO_COLLECTION_NAME = "masc_clean_dev"
ROOT_DOWNLOAD_PATH = Path(f"/mnt/volume_sfo3_01/data/{TARGET_SET}")
AUDIO_DOWNLOAD_PATH = Path("../data/clean_val/audios")
AUDIO_SEGMENT_DOWNLOAD_PATH = ROOT_DOWNLOAD_PATH / "audio_segments"

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


def process_audio(audio: Audio):
    audio_path = AUDIO_DOWNLOAD_PATH / f"{audio.audio_id}.wav"
    for segment in split_audio(
        audio_path=audio_path,
        audio_meta=audio,
        output_dir=AUDIO_SEGMENT_DOWNLOAD_PATH,
    ):
        pass


def insert_audio_segments(audio: Audio, target_audio_collection: AudioCollection):
    masc_audios = [MASCAudio.from_audio_segment(segment).dict() for segment in audio.audio_segments]
    target_audio_collection.insert_many(masc_audios)


def main():
    logging.info("Trying to connect to db.")
    audio_db = initialize_db()
    source_audio_collection = audio_db.get_collection(TARGET_SET)
    target_audio_collection = audio_db.get_collection(AUDIO_COLLECTION_NAME)
    all_audios = [
        Audio.from_dict(audio) for audio in source_audio_collection.find_all()
    ]
    # run multi-threaded for prcoessing audio
    # print(f"Total number of cpus: {cpu_count()}")
    # with Pool(cpu_count()) as p:
    #     list(tqdm(p.imap(process_audio,all_audios), total=len(all_audios)))
    # insert audio segments to db
    for audio in tqdm(all_audios, total=len(all_audios)):
        insert_audio_segments(audio, target_audio_collection)


if __name__ == "__main__":
    main()
