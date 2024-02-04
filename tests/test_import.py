"""Test mymongo."""

from pydantic import BaseModel

import mymongo
from mymongo import Document, Store


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(mymongo.__name__, str)
    assert issubclass(Document, BaseModel)
    assert isinstance(Store, type)
