from aioresponses import aioresponses
import pytest


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as mocked:
        yield mocked
