#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import List, Dict, TypeVar

from dataclasses import dataclass, field
from dateutil.relativedelta import relativedelta


@dataclass
class Account:
    _directory_download_home: Path
    id: str
    name: str
    path_directory_download: Path = field(init=False)
    latest_file_datetime: datetime = field(init=False)

    def __post_init__(self):
        self.path_directory_download = self._directory_download_home / (self.name + str(self.id))
        self.path_directory_download.mkdir(parents=True, exist_ok=True)
        files = sorted(self.path_directory_download.glob('*.*'), reverse=True)
        self.latest_file_datetime = datetime(1970, 1, 1, 0, 0, 0) if not files else self.extract_datetime(files[0])

    @staticmethod
    def extract_datetime(file) -> datetime:
        latest_file_name = file.name
        return datetime(
            int(latest_file_name[0: 4]),
            int(latest_file_name[4: 6]),
            int(latest_file_name[6: 8]),
            int(latest_file_name[8: 10]),
            int(latest_file_name[10: 12]),
            int(latest_file_name[12: 14])
        )

    def is_target_month(self, month: datetime) -> bool:
        return self.latest_file_datetime < month + relativedelta(months=1)

    def is_target_diary(self, created_datetime: datetime) -> bool:
        return self.latest_file_datetime < created_datetime


@dataclass
class AccountIterator:
    """This class implements configuration for account."""
    accounts: List[Dict[str, str]]
    directory_download: Path

    def __iter__(self):
        for account_id, account_name in self.accounts:
            # noinspection PyArgumentList
            yield Account(self.directory_download, account_id, account_name)


TypeVarAccount = TypeVar('TypeVarAccount', bound=Account)
