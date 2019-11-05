from abc import abstractmethod
from datetime import datetime


class FileNameBuilder:
    @staticmethod
    @abstractmethod
    def build(created_date_time: datetime, url: str) -> str:
        raise NotImplementedError()


class DefaultFileNameBuilder(FileNameBuilder):
    @staticmethod
    def build(created_date_time: datetime, url: str) -> str:
        file_name = url.replace('https://', created_date_time.strftime('%Y%m%d%H%M%S')).replace('/', '_')
        index_question = file_name.find('?')
        if index_question >= 0:
            file_name = file_name[:index_question]
        return file_name
