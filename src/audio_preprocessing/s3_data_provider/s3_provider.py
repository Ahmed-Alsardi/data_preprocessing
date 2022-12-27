import boto3
from dotenv import load_dotenv
from pathlib import Path
import os
from typing import Generator
from dataclasses import dataclass
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

load_dotenv()

ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
SECRET_KEY = os.environ['AWS_SECRET_KEY']
SUBTITLE_PREFIX = 'masc/clean_train/subtitles'
SUBTITLE_DOWNLOAD_PATH = Path.cwd() / 'subtitles'
BUCKET_NAME = "arabic-speech-data"


@dataclass(kw_only=True)
class S3Config:
    access_key: str
    secret_key: str
    subtitle_prefix: str
    bucket_name: str


class S3SubtitleProvider:
    def __init__(self, s3_config: S3Config, subtitle_download_path: Path):
        self._s3_config = s3_config
        self._subtitle_download_path = subtitle_download_path
        # Create a session
        logging.info('Accessing S3...')
        self._session: boto3.Session = boto3.Session(
            aws_access_key_id=self._s3_config.access_key,
            aws_secret_access_key=self._s3_config.secret_key,
        )
        # Create a resource
        self._s3 = self._session.resource('s3')
        self._bucket = self._s3.Bucket(self._s3_config.bucket_name)
        # Get the list of subtitles
        self._subtitle_list: list[str] = self._get_subtitle_list()
        logging.info(f"Total number of subtitles: {len(self._subtitle_list)}")

    @property
    def subtitle_list(self) -> list[str]:
        return self._subtitle_list

    def download_subtitles(self) -> Generator[Path, None, None]:
        """
        Generator that yields the path to the downloaded subtitle.
        :return: List of paths to downloaded subtitles.
        """
        print("Downloading subtitles...")
        for subtitle in self._subtitle_list:
            self._bucket.download_file(subtitle, self._subtitle_download_path / subtitle.split('/')[-1])
            yield self._subtitle_download_path / subtitle.split('/')[-1]

    def _get_subtitle_list(self) -> list[str]:
        subtitle_list: list[str] = []
        logging.info("Retrieving subtitles...")
        for page in self._bucket.objects.filter(
                Prefix=self._s3_config.subtitle_prefix).pages():
            [subtitle_list.append(o.key) for o in page]
            logging.info(f"Retrieved {len(subtitle_list)} subtitles")
        return subtitle_list


if __name__ == '__main__':
    logging.info('initiating S3SubtitleProvider...')
    s3_config = S3Config(
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        subtitle_prefix=SUBTITLE_PREFIX,
        bucket_name=BUCKET_NAME
    )
    s3 = S3SubtitleProvider(s3_config=s3_config, subtitle_download_path=SUBTITLE_DOWNLOAD_PATH)
    logging.info(f"First 3 subtitles: {s3.subtitle_list[:3]}")
    logging.info('Downloading subtitles...')
    for i, subtitle_path in enumerate(s3.download_subtitles()):
        if i == 5:
            break
        logging.info(f"Downloaded subtitle {i}: {subtitle_path}")
