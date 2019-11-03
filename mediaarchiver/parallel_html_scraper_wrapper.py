from typing import Generic, Iterable, Optional

from parallelhtmlscraper import ParallelHtmlScraper
from parallelhtmlscraper.html_analyzer import HtmlAnalyzer

from mediaarchiver.post_processor import T, U, PostProcessor, Flattener


class ParallelHtmlScraperWrapper(Generic[T, U]):
    @classmethod
    def execute(
            cls,
            base_url: str,
            list_url_monthly_archive_page: Iterable[str],
            analyzer: HtmlAnalyzer[T],
            *,
            limit: int,
            post_processor: Optional[PostProcessor[T, U]] = None
    ) -> U:
        processor = cls.set_default(post_processor)
        list_analyze_result = ParallelHtmlScraper.execute(
            base_url, list_url_monthly_archive_page, analyzer, limit=limit
        )
        return processor.execute(list_analyze_result)

    @classmethod
    def set_default(cls, processor: Optional[PostProcessor[T, U]]) -> PostProcessor[T, U]:
        return Flattener() if processor is None else processor
