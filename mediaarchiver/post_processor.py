from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar, Optional

# pylint: disable=invalid-name
T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


class PostProcessor(Generic[T, U], ABC):
    @abstractmethod
    def execute(self, list_: List[T]) -> U:
        raise NotImplementedError()


class Flattener(PostProcessor):
    def execute(self, list_: List[List[V]]) -> List[V]:
        return [flatten for inner in list_ for flatten in inner]


class DuplicateRemover(Flattener):
    def __init__(self, list_: Optional[List[V]] = None):
        self.list_: List[V] = [] if list_ is None else list_

    def execute(self, list_: List[List[V]]) -> List[V]:
        self.list_.extend(super().execute(list_))
        return list(set(self.list_))
