#!/usr/bin/env python
"""This module implements archiving steps for media files at some of web site."""
from __future__ import annotations
from abc import abstractmethod, ABC
import copy
from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from typing import List, Generic, Iterable, Type, Callable
# noinspection PyProtectedMember
from urllib import request
from urllib.error import HTTPError

from bs4 import BeautifulSoup
from parallelhtmlscraper.html_analyzer import HtmlAnalyzer

from mediaarchiver import CONFIG
from mediaarchiver.article import Article
from mediaarchiver.config import SiteConfig
from mediaarchiver.htmlanalyzer.article_analyzer import ArticleAnalyzer, ClueArticle
from mediaarchiver.htmlanalyzer.article_page_url_analyzer import ArticlePageUrlAnalyzer
from mediaarchiver.models import TypeVarAccount
from mediaarchiver.parallel_html_scraper_wrapper import ParallelHtmlScraperWrapper
from mediaarchiver.post_processor import DuplicateRemover


class MonthlyArchiveUrlAnalyzer(HtmlAnalyzer):
    async def execute(self, soup: BeautifulSoup) -> List[str]:
        raise NotImplementedError()


class BlogHomeUrlBuilder(Generic[TypeVarAccount]):
    @classmethod
    def build_blog_home_url(cls, account: TypeVarAccount) -> str:
        raise NotImplementedError()


class ArticlePageUrlListUpTask(Generic[TypeVarAccount]):
    def execute(self, account: TypeVarAccount, soup_diary_home_page: BeautifulSoup) -> List[str]:
        raise NotImplementedError()


@dataclass
class WebSiteContext:
    config: Callable[[], SiteConfig]
    base_url: str
    limit: int = 5


@dataclass
class NonTimeLineBlogSiteContext:
    web_site_context: WebSiteContext
    clue_article: ClueArticle
    blog_home_url_builder: BlogHomeUrlBuilder
    article_page_url_list_up_task: Callable[[], ArticlePageUrlListUpTask]


class NonTimeLineBlogSiteArticlePageUrlListUpTask(ArticlePageUrlListUpTask):
    def __init__(
            self,
            web_site_context: WebSiteContext,
            monthly_archive_home_page_url_extractor: MonthlyArchiveHomePageUrlExtractor,
            monthly_archive_page_url_list_up_task: AbstractMonthlyArchivePageUrlListUpTask,
            article_page_analyzer: Type[ArticlePageUrlAnalyzer]
    ):
        self.web_site_context = web_site_context
        self.monthly_archive_home_page_url_extractor = monthly_archive_home_page_url_extractor
        self.monthly_archive_page_url_list_up_task = monthly_archive_page_url_list_up_task
        self.article_page_analyzer = article_page_analyzer
        self.logger = getLogger(__name__)

    def execute(self, account: TypeVarAccount, soup_diary_home_page: BeautifulSoup) -> List[str]:
        self.logger.info('start extract_url_monthly_archive_home_page')
        list_url_monthly_archive_home_page = self.monthly_archive_home_page_url_extractor.execute(
            soup_diary_home_page, account
        )
        self.logger.info('finish extract_url_monthly_archive_home_page')
        self.logger.debug(list_url_monthly_archive_home_page)
        self.logger.info('start MONTHLY_ARCHIVE_PAGE_URL_LIST_UP_TASK')
        list_url_monthly_archive_page = self.monthly_archive_page_url_list_up_task.execute(
            list_url_monthly_archive_home_page
        )
        self.logger.info('finish MONTHLY_ARCHIVE_PAGE_URL_LIST_UP_TASK')
        self.logger.debug(list_url_monthly_archive_page)
        self.logger.info('start list_up_url_article_page_by_monthly_archive_page')
        list_url_article: List[str] = ParallelHtmlScraperWrapper.execute(
            self.web_site_context.base_url,
            list_url_monthly_archive_page,
            self.article_page_analyzer(account),
            limit=self.web_site_context.limit,
            post_processor=DuplicateRemover()
        )
        self.logger.info('finish list_up_url_article_page_by_monthly_archive_page')
        return list_url_article


class BlogSite(Generic[TypeVarAccount], ABC):
    """This class implements archiving steps for media files at some of web site."""
    def __init__(self, web_site_context: WebSiteContext):
        self.web_site_context = web_site_context

    @abstractmethod
    def list_up_article(self, account):
        raise NotImplementedError()


class NonTimeLineBlogSite(BlogSite):
    def __init__(self, non_time_line_blog_site_context: NonTimeLineBlogSiteContext):
        super().__init__(non_time_line_blog_site_context.web_site_context)
        self.non_time_line_blog_site_context = non_time_line_blog_site_context
        self.logger = getLogger(__name__)

    def list_up_article(self, account) -> List[Article]:
        self.logger.info('start request_diary_home_page')
        soup_diary_home_page = self.__request_diary_home_page(account)
        self.logger.info('finish request_diary_home_page')
        self.logger.info('start list_up_url_article_page')
        list_url_article_page = self.non_time_line_blog_site_context.article_page_url_list_up_task(  # type: ignore
            # Reason: @see https://github.com/python/mypy/issues/6910
        ).execute(
            account, soup_diary_home_page
        )
        self.logger.info('finish list_up_url_article_page')
        self.logger.debug(list_url_article_page)
        self.logger.info('start analyze_article')
        list_article: List[Article] = ParallelHtmlScraperWrapper.execute(
            self.web_site_context.base_url,
            list_url_article_page,
            ArticleAnalyzer(self.non_time_line_blog_site_context.clue_article),
            limit=self.web_site_context.limit
        )
        self.logger.info('finish analyze_article')
        return list_article

    def __request_diary_home_page(self, account: TypeVarAccount) -> BeautifulSoup:
        diary_home_url = (f'{self.web_site_context.base_url}'
                          f'{self.non_time_line_blog_site_context.blog_home_url_builder.build_blog_home_url(account)}')
        # Reason: @see https://github.com/PyCQA/pylint/issues/2395 pylint: disable=logging-fstring-interpolation
        self.logger.info(f'request = {diary_home_url}')
        try:
            return BeautifulSoup(request.urlopen(diary_home_url), "html.parser")
        except HTTPError as error:
            if error.code == 404:
                raise HTTPError(
                    error.url,
                    error.code,
                    (f'Account may be removed. account.name = {account.name}, '
                     'account.id = {account.id}. {error.msg}'),  # type: ignore
                    error.hdrs,  # type: ignore
                    error.fp  # type: ignore
                    # Reason: Wrong type information from urllib
                )
            raise error


class MonthlyArchiveHomePageUrlExtractor(Generic[TypeVarAccount]):
    def execute(self, soup: BeautifulSoup, account: TypeVarAccount) -> List[str]:
        raise NotImplementedError()


class AbstractMonthlyArchivePageUrlListUpTask:
    def __init__(self, web_site_context: WebSiteContext):
        self.web_site_context = web_site_context

    def execute(self, list_url_monthly_archive_home_page: List[str]) -> Iterable[str]:
        raise NotImplementedError()


class MonthlyArchivePageUrlListUpTask(AbstractMonthlyArchivePageUrlListUpTask):
    def __init__(self, web_site_context: WebSiteContext, monthly_archive_url_analyzer: MonthlyArchiveUrlAnalyzer):
        super().__init__(web_site_context)
        self.monthly_archive_url_analyzer = monthly_archive_url_analyzer

    def execute(self, list_url_monthly_archive_home_page: List[str]) -> Iterable[str]:
        return ParallelHtmlScraperWrapper.execute(
            self.web_site_context.base_url,
            list_url_monthly_archive_home_page,
            self.monthly_archive_url_analyzer,
            limit=self.web_site_context.limit,
            post_processor=DuplicateRemover(copy.copy(list_url_monthly_archive_home_page))
        )


class Site(Enum):
    TWITTER = WebSiteContext(
        lambda: CONFIG.twitter,
        'https://api.twitter.com/2/timeline/media',
        1,
    )
