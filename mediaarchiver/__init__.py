#!/usr/bin/env python
from enum import Enum
from pathlib import Path

from mediaarchiver.config import Config

CONFIG: Config = Config()


class Directory(Enum):
    """
    This class implements constant of path_directory_download to directory of CSV.
    """
    DOWNLOAD = Path(__file__).parent.parent / 'download'

    @property
    def value(self) -> Path:
        """This method overwrite super method for type hint."""
        return super().value
