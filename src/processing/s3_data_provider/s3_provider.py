import boto3
from dotenv import load_dotenv
from pathlib import Path
import os
from typing import Generator
from dataclasses import dataclass
import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

load_dotenv()

ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
SECRET_KEY = os.environ["AWS_SECRET_KEY"]
SUBTITLE_PREFIX = "masc/clean_train/subtitles"
AUDIO_PREFIX = "masc/clean_train/audios"
SUBTITLE_DOWNLOAD_PATH = Path.cwd().parent / "data" / "subtitles"
AUDIO_DOWNLOAD_PATH = Path.cwd().parent / "data" / "audios"
BUCKET_NAME = "arabic-speech-data"


@dataclass(kw_only=True)
class S3Config:
    access_key: str
    secret_key: str
    folder_prefix: str
    bucket_name: str


class AWSS3:
    def __init__(self, s3_config: S3Config):
        self._s3_config = s3_config
        # Create a session
        logging.info("Accessing S3...")
        self._session: boto3.Session = boto3.Session(
            aws_access_key_id=self._s3_config.access_key,
            aws_secret_access_key=self._s3_config.secret_key,
        )
        # Create a resource
        self._s3 = self._session.resource("s3")
        self._bucket = self._s3.Bucket(self._s3_config.bucket_name)

    @property
    def folder_prefix(self) -> str:
        return self._s3_config.folder_prefix


class S3AudioProvider(AWSS3):
    def __init__(self, s3_config: S3Config, audio_download_path: Path):
        super().__init__(s3_config)
        self._audio_download_path = audio_download_path
        # Get the list of audio files

    def download(self, filename: str) -> Path:
        """
        Download a single audio file.
        :param filename: Name of the audio file to download.
        :return: Path to the downloaded audio file.
        """
        target_path = self._audio_download_path / filename
        source_file = f"{self.folder_prefix}/{filename}"
        self._bucket.download_file(source_file, target_path)
        return target_path


class S3SubtitleProvider(AWSS3):
    def __init__(self, s3_config: S3Config, subtitle_download_path: Path):
        super().__init__(s3_config)
        self._subtitle_download_path = subtitle_download_path
        # Get the list of subtitles
        self._subtitle_list: list[str] = self._get_subtitle_list()
        logging.info(f"Total number of subtitles: {len(self._subtitle_list)}")

    @property
    def subtitle_list(self) -> list[str]:
        return self._subtitle_list

    def download_subtitles(self) -> Generator[Path, None, None]:
        """
        Generator that yields the path to the downloaded subtitles.
        :return: List of paths to downloaded subtitles.
        """
        print("Downloading subtitles...")
        for subtitle in self._subtitle_list:
            file_path = self._subtitle_download_path / subtitle.split("/")[-1]
            self._bucket.download_file(subtitle, file_path)
            yield file_path

    def _get_subtitle_list(self) -> list[str]:
        subtitle_list: list[str] = []
        logging.info("Retrieving subtitles...")
        for page in self._bucket.objects.filter(
            Prefix=self._s3_config.folder_prefix
        ).pages():
            [subtitle_list.append(o.key) for o in page]
            logging.info(f"Retrieved {len(subtitle_list)} subtitles")
        return subtitle_list


if __name__ == "__main__":
    logging.info("initiating S3SubtitleProvider...")
    s3_config = S3Config(
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        folder_prefix=AUDIO_PREFIX,
        bucket_name=BUCKET_NAME,
    )
    s3 = S3AudioProvider(s3_config=s3_config, audio_download_path=AUDIO_DOWNLOAD_PATH)
    logging.info("Downloading audios...")
    s3.download("-0CPXg6LyYA.wav")
