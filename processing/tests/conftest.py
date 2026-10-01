import os
from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def base_path() -> Path:
    return Path(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def data_path(base_path) -> Path:
    return base_path / 'data'
