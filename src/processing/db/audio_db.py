import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
from dataclasses import dataclass
import logging
from processing.db.models import AudioDocument, DOCUMENT_LIST, AudioSegment
from processing.services.splitting_vtt import Audio

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

load_dotenv()

MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")


@dataclass(kw_only=True)
class DBConfig:
    username: str
    password: str
    host: str = "localhost"
    port: int = 27017
    db_name: str

    @property
    def uri(self):
        return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"


async def connect_to_mongo(db_config: DBConfig, document_models: list):
    client = AsyncIOMotorClient(db_config.uri)
    await init_beanie(database=client[db_config.db_name], document_models=document_models)


def convert_audio_to_document(audio: Audio) -> AudioDocument:
    """
    a helper function to convert an Audio object to an AudioDocument object
    :param audio:
    :return: AudioDocument object
    """
    return AudioDocument(audio_id=audio.audio_id,
                         audio_segments=audio.audio_segments,
                         audio_length=audio.audio_length)


async def save_audio(audio: Audio | AudioDocument) -> None:
    """
    Save an audio object to the database
    :param audio:
    :return None
    """
    if isinstance(audio, Audio):
        audio = convert_audio_to_document(audio)
    await audio.insert()


async def main():
    """For testing purposes"""
    db_config = DBConfig(username=MONGODB_USERNAME, password=MONGODB_PASSWORD, db_name="testing_db1")
    await connect_to_mongo(db_config=db_config, document_models=DOCUMENT_LIST)
    sub_segment = AudioSegment(start=0, end=100, text="Hello world")
    audio_segment = AudioDocument(audio_id="123", audio_segments=[sub_segment], audio_length=100)
    await save_audio(audio_segment)
    logging.info("Audio was saved in db")
    audio = await AudioDocument.find_one(AudioDocument.audio_id == "123")
    logging.info(f"Audio {audio} was retrieved from db")


if __name__ == '__main__':
    asyncio.run(main())
