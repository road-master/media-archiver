
from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig

from mediaarchiver.models import AccountIterator


# noinspection Pylint
# @see https://github.com/python/mypy/issues/5374
@dataclass
class SiteConfig(DataClassJsonMixin):  # type: ignore
    """This class implements configuration for account."""
    @abstractmethod
    def account_iterator(self, directory_download: Path):
        raise NotImplementedError()


@dataclass
class TwitterConfig(SiteConfig):
    """This class implements configuration for DTO."""
    accounts: List[Dict[str, str]]

    def account_iterator(self, directory_download: Path):
        return AccountIterator(self.accounts, directory_download)


@dataclass
class Config(YamlDataClassConfig):
    """This class implements configuration wrapping."""
    twitter: TwitterConfig = field(  # type: ignore
        default=None,
        metadata={'dataclasses_json': {'mm_field': TwitterConfig}}
    )
