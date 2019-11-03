#!/usr/bin/env python
"""
TODO Twitter のバックエンドの仕様が変わり、 request 先の URL と戻りの JSON が変わったので作りなおし
"""
import json
from datetime import datetime
from logging import getLogger
from typing import List, Optional, Dict
from urllib import request

from bs4 import BeautifulSoup

from mediaarchiver.article import Article
from mediaarchiver.models import Account, TypeVarAccount
from mediaarchiver.sites import BlogSite, WebSiteContext


class Position:
    def __init__(self, web_site_context: WebSiteContext, account: Account):
        self.article_home_url: str = f'{web_site_context.base_url}{self.build_blog_home_url(account)}'
        self.current_url: str = self.article_home_url
        self.current: str = ''
        self._is_updated: Optional[bool] = None
        self.logger = getLogger(__name__)
        # Reason: @see https://github.com/PyCQA/pylint/issues/2395 pylint: disable=logging-fstring-interpolation
        self.logger.debug(f'request = {self.article_home_url}')

    def move(self, new_position):
        self._is_updated = self.current != new_position
        self.current = new_position
        self.current_url = f'{self.article_home_url}&cursor={new_position}'

    @property
    def is_updated(self):
        return self.is_updated or self.is_updated is None

    @classmethod
    def build_blog_home_url(cls, account: Account) -> str:
        return '/' + account.id + '.json' + \
               '?include_profile_interstitial_type=1' + \
               '&include_blocking=1' + \
               '&include_blocked_by=1' + \
               '&include_followed_by=1' + \
               '&include_want_retweets=1' + \
               '&include_mute_edge=1' + \
               '&include_can_dm=1' + \
               '&include_can_media_tag=1' + \
               '&skip_status=1' + \
               '&cards_platform=Web-12' + \
               '&include_cards=1' + \
               '&include_composer_source=true' + \
               '&include_ext_alt_text=true' + \
               '&include_reply_count=1' + \
               '&tweet_mode=extended' + \
               '&include_entities=true' + \
               '&include_user_entities=true' + \
               '&include_ext_media_color=true' + \
               '&include_ext_media_availability=true' + \
               '&send_error_codes=true' + \
               '&count=20' + \
               '&ext=mediaStats%2ChighlightedLabel%2CcameraMoment'


class TimelineScanner:
    def __init__(self, web_site_context: WebSiteContext, account: Account):
        self.list_article: List[Article] = []
        self.position = Position(web_site_context, account)

    def scan_timeline(self):
        response = request.urlopen(self.position.current_url)
        json_response = json.loads(response.read().decode('utf8'))
        self.list_article.extend(self.extract_article(json_response))
        new_position = self.extract_position(json_response)
        self.position.move(new_position)

    @classmethod
    def extract_position(cls, json_response: Dict) -> str:
        last_entry = json_response['timeline']['instructions'][0]['addEntries']['entries'][-1]
        new_position = last_entry['content']['operation']['cursor']['value']
        return new_position

    @classmethod
    def extract_article(cls, json_response: Dict) -> List[Article]:
        tweets = json_response['globalObjects']['tweets']
        temp_list_article = []
        for tweet in tweets.values():
            created_date_time = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
            list_url_media = [media['media_url_https'] for media in tweet['entities']['media']]
            temp_list_article.append(Article(created_date_time, list_url_media))
        return temp_list_article


class Twitter(BlogSite):
    def __init__(self, web_site_context: WebSiteContext):
        super().__init__(web_site_context)
        self.logger = getLogger(__name__)

    @classmethod
    def list_up_url_article_page(cls, account: TypeVarAccount, soup_diary_home_page: BeautifulSoup) -> List[str]:
        raise NotImplementedError()

    def list_up_article(self, account: Account) -> List[Article]:
        time_line_scanner = TimelineScanner(self.web_site_context, account)
        while time_line_scanner.position.is_updated:
            time_line_scanner.scan_timeline()
        return time_line_scanner.list_article
