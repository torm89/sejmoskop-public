import os
from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def statements_data_path() -> Path:
    return Path(os.path.dirname(__file__)) / '..' / '..' / 'data' / 'statements'


@pytest.fixture(scope='session')
def true_data_path() -> Path:
    return Path(os.path.dirname(__file__)) / '..' / '..' / 'data' / 'true'
