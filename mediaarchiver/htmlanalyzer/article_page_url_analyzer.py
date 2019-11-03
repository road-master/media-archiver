from abc import ABC
from parallelhtmlscraper.html_analyzer import HtmlAnalyzer
from mediaarchiver.models import TypeVarAccount


# Reason: Pylint's Bug. @see https://github.com/PyCQA/pylint/issues/179 pylint: disable=abstract-method
class ArticlePageUrlAnalyzer(HtmlAnalyzer, ABC):
    def __init__(self, account: TypeVarAccount):
        self.account = account
