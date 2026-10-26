import inspect
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from aiohttp import ClientResponse
from aioresponses import aioresponses

if TYPE_CHECKING:
    from collections.abc import Generator

    from pytest_mock import MockerFixture


def supply_stream_writer_to_client_response(mocker: "MockerFixture") -> None:
    """Supply the stream_writer argument that aioresponses omits when building ClientResponse.

    aiohttp 3.14 added the required keyword-only argument ``stream_writer`` to ``ClientResponse.__init__``,
    but aioresponses 0.7.9 doesn't pass it, so every mocked request raises TypeError.
    aiohttp only reads ``stream_writer.output_size`` from it.
    Remove this once aioresponses releases the fix: https://github.com/pnuckowski/aioresponses/issues/289
    """
    original_init = ClientResponse.__init__
    if "stream_writer" not in inspect.signature(original_init).parameters:
        return

    def init_with_stream_writer(self: ClientResponse, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("stream_writer", Mock(output_size=0))
        original_init(self, *args, **kwargs)

    mocker.patch.object(ClientResponse, "__init__", init_with_stream_writer)


@pytest.fixture
def mock_aioresponse(mocker: "MockerFixture") -> "Generator[aioresponses, None, None]":
    supply_stream_writer_to_client_response(mocker)
    with aioresponses() as mocked:
        yield mocked
