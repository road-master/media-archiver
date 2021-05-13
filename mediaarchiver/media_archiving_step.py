#!/usr/bin/env python
"""This module implements archiving steps for media files at some of web site."""
from logging import getLogger
from pathlib import Path
from traceback import format_tb
from typing import Generic, List, Tuple, TypeVar

from parallelmediadownloader.modeia_download_result import MediaDownloadResult
from parallelmediadownloader.parallel_media_downloader import ParallelMediaDownloader

from mediaarchiver.download_order_generator import DownloadOrderGenerator
from mediaarchiver.micro_image_filter import MicroImageFilter
from mediaarchiver.models import Account
from mediaarchiver.sites import BlogSite

TypeVarAccount = TypeVar("TypeVarAccount", bound=Account)


class MediaArchivingStep(Generic[TypeVarAccount]):
    """This class implements archiving steps for media files at some of web site."""

    def __init__(self, blog_site: BlogSite):
        self.blog_site = blog_site
        self.logger = getLogger(__name__)

    def execute(self, directory_download: Path) -> None:
        """This method executes all CSV converters."""
        list_download_result: List[MediaDownloadResult] = []
        list_exception: List[Tuple[TypeVarAccount, Exception]] = []
        for account in self.blog_site.web_site_context.config().account_iterator(directory_download):  # type: ignore
            # Reason @see https://github.com/python/mypy/issues/6910
            try:
                list_download_result.extend(self.execute_per_account(account))
            # Reason: To prevent to stop process for other account. pylint: disable=broad-except
            except Exception as error:
                list_exception.append((account, error))
        for download_result in list_download_result:
            self.logger.info(f"Status = {download_result.status}, URL = {download_result.url}")
        if list_exception:
            for (account, exception) in list_exception:
                list_trace_back = "".join(format_tb(exception.__traceback__))
                # Reason: @see https://github.com/PyCQA/pylint/issues/2395 pylint: disable=logging-fstring-interpolation
                self.logger.error(f"Account = {account.id}:{account.name}")
                self.logger.exception(f"{exception}\n{list_trace_back}")
            raise Exception("Some exception raised.")

    def execute_per_account(self, account: TypeVarAccount) -> List[MediaDownloadResult]:
        """This method executes all CSV converters."""
        self.logger.info("start list_up_article")
        list_article = self.blog_site.list_up_article(account)
        self.logger.info("finish list_up_article")
        self.logger.debug(list_article)
        self.logger.info("start download_as_parallel")
        download_order_generator = DownloadOrderGenerator(
            self.blog_site.web_site_context.base_url, account.path_directory_download, list_article
        )
        list_download_result = ParallelMediaDownloader.execute(
            download_order_generator,
            limit=self.blog_site.web_site_context.limit,
            media_filter=MicroImageFilter(),
            allow_http_status=[404],
        )
        self.logger.info("finish download_as_parallel")
        return [download_result for download_result in list_download_result if download_result.status != 200]
