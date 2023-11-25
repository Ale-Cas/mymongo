"""Test mymongo."""

import mymongo


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(mymongo.__name__, str)
