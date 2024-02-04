"""Test the Document class."""
from collections.abc import Generator
from typing import Any

import pytest
from mongomock import Collection, MongoClient


@pytest.fixture()
def mock_collection() -> Generator[Collection, None, None]:
    """Mock collection fixture."""
    client: MongoClient[dict[str, Any]] = MongoClient()
    _test_name = "test"
    yield client.get_database(name=_test_name).get_collection(name=_test_name)
    client.drop_database(_test_name)
