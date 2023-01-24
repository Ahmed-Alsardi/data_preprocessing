import os
from dotenv import load_dotenv
from dataclasses import dataclass
import logging
from pymongo import MongoClient
from pymongo.collection import Collection
# mongo object id
from bson.objectid import ObjectId

from processing.db.models import Audio

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

load_dotenv()

MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_HOST = os.getenv("MONGODB_HOST")


@dataclass(kw_only=True)
class DBConfig:
    username: str
    password: str
    host: str = "localhost"
    port: int = 27017
    db_name: str
    protocol_name: str = "mongodb+srv"

    @property
    def uri(self):
        return f"{self.protocol_name}://{self.username}:{self.password}@{self.host}/?retryWrites=true&w=majority"



class AudioCollection:
    def __init__(self, collection: Collection):
        self.collection = collection
    
    def insert_one(self, audio: Audio) -> ObjectId:
        # check if audio already exists
        if docuemtn:= self.collection.find_one({"audio_id": audio.audio_id}):
            return docuemtn["_id"]
        return self.collection.insert_one(audio.dict())
    
    def insert_many(self, audios: list[Audio]) -> list[ObjectId]:
        return [self.insert_one(audio) for audio in audios]


class MongoDB:
    def __init__(self, config: DBConfig):
        self.config = config
        self.client = MongoClient(self.config.uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[self.config.db_name]

    def get_collection(self, collection_name: str) -> AudioCollection :
        return AudioCollection(collection=self.db[collection_name])

    def get_all_collections(self) -> list[str]:
        return self.db.list_collection_names()


if __name__ == "__main__":
    config = DBConfig(
        username=MONGODB_USERNAME,
        password=MONGODB_PASSWORD,
        host=MONGODB_HOST,
        db_name="test",
    )
    db = MongoDB(config)
    try:
        print(db.client.server_info())
        print(type(db.get_collection("test")))
    except Exception as e:
        print(e)
