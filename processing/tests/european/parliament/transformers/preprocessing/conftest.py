from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def reference_european_parliament_transformers_processing_path(reference_european_parliament_path) -> Path:
    return reference_european_parliament_path / 'transformers' / 'processing'
