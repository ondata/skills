"""Shared fixtures for open-data-quality tests."""

from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fx():
    """Return a helper that resolves a fixture file path."""
    def _get(name: str) -> Path:
        return FIXTURES / name
    return _get
