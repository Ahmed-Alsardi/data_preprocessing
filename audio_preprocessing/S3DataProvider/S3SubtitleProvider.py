import boto3
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
SECRET_KEY = os.environ['AWS_SECRET_KEY']
SUBTITLE_PREFIX = 'masc/clean_train/subtitles'
SUBTITLE_DOWNLOAD_PATH = Path.cwd() / 'subtitles'


class S3SubtitleProvider:
    def __init__(self, access_key: str, secret_key: str, subtitle_prefix: str,
                 subtitle_download_path: Path, bucket_name: str = 'arabic-speech-data',
                 page_size: int = 5):
        self._subtitle_prefix = subtitle_prefix
        self._subtitle_download_path = subtitle_download_path
        self._bucket_name = bucket_name
        self._page_size = page_size
        # Create a session
        print('Accessing S3...')
        self._session: boto3.Session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        # Create a resource
        self._s3 = self._session.resource('s3')
        self._bucket = self._s3.Bucket(self._bucket_name)
        # Get the list of subtitles
        self._subtitle_list: list[str] = self._get_subtitle_list()
        print(f"Total number of subtitles: {len(self._subtitle_list)}")

    def _get_subtitle_list(self, page_size=100) -> list[str]:
        subtitle_list: list[str] = []
        print("Retrieving subtitles...")
        for i, page in enumerate(self._bucket.objects.filter(
                Prefix=self._subtitle_prefix).page_size(page_size).pages()):
            [subtitle_list.append(o.key) for o in page]
            print(f"Retrieved {len(subtitle_list)} subtitles")
        return subtitle_list


if __name__ == '__main__':
    print('initiating S3SubtitleProvider...')
    s3 = S3SubtitleProvider(ACCESS_KEY, SECRET_KEY, SUBTITLE_PREFIX, SUBTITLE_DOWNLOAD_PATH)
    print(f"First 3 subtitles: {s3._subtitle_list[:3]}")
