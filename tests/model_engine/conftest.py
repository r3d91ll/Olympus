"""Test fixtures for model engine tests."""
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def cleanup_test_models():
    """Clean up test models directory."""
    test_dir = Path("/tmp/test_models")
    if test_dir.exists():
        for item in test_dir.iterdir():
            if item.is_file():
                item.unlink()
            else:
                for subitem in item.iterdir():
                    subitem.unlink()
                item.rmdir()
        test_dir.rmdir()
    yield
