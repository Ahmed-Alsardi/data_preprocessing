import os
from dotenv import load_dotenv
from dataclasses import dataclass
import logging

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
    protocol_name: str = "mongodb+srv"

    @property
    def uri(self):
        return f"{self.protocol_name}://{self.username}:{self.password}@{self.host}:{self.port}"

