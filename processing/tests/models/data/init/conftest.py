from typing import Dict, List
from unittest.mock import Mock

import pandas as pd
import pytest

from processing.models.data import DataHot, Data


class MockDataHot(DataHot):
    pass


class MockData(Data):
    @property
    def columns(self) -> List[str]:
        return []

    @property
    def columns_types(self) -> Dict[str, str]:
        return {}


@pytest.fixture
def mock_data():
    return MockData(tag=Mock(), df=pd.DataFrame())
