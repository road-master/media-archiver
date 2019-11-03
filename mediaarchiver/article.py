#!/usr/bin/env python
from datetime import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class Article:
    created_date_time: datetime
    list_url_media: List[str]
