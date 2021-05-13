from dataclasses import dataclass
from datetime import datetime
from typing import List

# noinspection PyProtectedMember
from bs4 import BeautifulSoup, Tag
from parallelhtmlscraper.html_analyzer import HtmlAnalyzer

from mediaarchiver.article import Article


class DatetimeExtractor:
    @classmethod
    def execute(cls, soup: BeautifulSoup, tag_article_area: Tag) -> datetime:
        raise NotImplementedError()


@dataclass
class ClueArticle:
    tag_article_area: str
    class_article_area: str
    datetime_extractor: DatetimeExtractor


class ArticleAnalyzer(HtmlAnalyzer):
    PIXEL_EMOJI_AMEBA_BLOG: int = 96

    def __init__(self, clue_article: ClueArticle):
        self.clue_article = clue_article

    async def execute(self, soup: BeautifulSoup) -> List[Article]:
        list_tag_article_area = soup.find_all(
            self.clue_article.tag_article_area, class_=self.clue_article.class_article_area
        )
        return [self.create_article(soup, tag) for tag in list_tag_article_area]

    def create_article(self, beautiful_soup: BeautifulSoup, tag_article_area: Tag) -> Article:
        list_url_image: List[str] = list(
            {
                image_tag.get("src")
                for image_tag in tag_article_area.find_all("img")
                if self.is_target_image_tag(image_tag)
            }
        )
        return Article(self.clue_article.datetime_extractor.execute(beautiful_soup, tag_article_area), list_url_image)

    @classmethod
    def is_target_image_tag(cls, image_tag: Tag) -> bool:
        return (
            image_tag.has_attr("src")
            and image_tag.get("src").find("//d-markets.net") == -1
            and (not image_tag.has_attr("width") or int(image_tag.get("width")) > cls.PIXEL_EMOJI_AMEBA_BLOG)
            and (not image_tag.has_attr("height") or int(image_tag.get("height")) > cls.PIXEL_EMOJI_AMEBA_BLOG)
            and (not image_tag.get("src").startswith("cid"))
        )
