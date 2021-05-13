from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional

from parallelmediadownloader.media_download_coroutine import DownloadOrder
from parallelmediadownloader.media_save_coroutine import SaveOrder

from mediaarchiver.article import Article
from mediaarchiver.file_name_builder import DefaultFileNameBuilder, FileNameBuilder


class DownloadOrderGenerator:
    def __init__(
        self,
        base_url: str,
        path_directory_download: Path,
        list_article: List[Article],
        file_name_builder: Optional[FileNameBuilder] = None,
    ):
        self.base_url = base_url
        self.path_directory_download = path_directory_download
        self.list_article = list_article
        self.file_name_builder = self.set_default(file_name_builder)

    @staticmethod
    def set_default(file_name_builder: Optional[FileNameBuilder]) -> FileNameBuilder:
        return DefaultFileNameBuilder() if file_name_builder is None else file_name_builder

    def __iter__(self) -> Generator[DownloadOrder, None, None]:
        for article in self.list_article:
            for url_media in article.list_url_media:
                yield self.create_coroutine(self.build_url(url_media), article.created_date_time)

    def create_coroutine(self, url: str, created_date_time: datetime) -> DownloadOrder:
        return DownloadOrder(
            url,
            SaveOrder(
                self.path_directory_download, self.file_name_builder.build(created_date_time, url), created_date_time
            ),
        )

    def build_url(self, url_media: str) -> str:
        if url_media.startswith("https://"):
            return url_media
        if url_media.startswith("HTTPS://"):
            return url_media.replace("HTTPS://", "https://", 1)
        if url_media.startswith("http://"):
            return url_media.replace("http://", "https://", 1)
        if url_media.startswith("HTTP://"):
            return url_media.replace("HTTP://", "https://", 1)
        if url_media.startswith("//"):
            return f"https:{url_media}"
        return self.base_url + url_media
