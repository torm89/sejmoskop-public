from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from pydantic import TypeAdapter

from processing.manager.batch import BatchManager
from processing.manager.batch.group import BatchManagerProcessingGroup
from processing.manager.batch.member import BatchManagerProcessingMember
from processing.manager.batch.statement import BatchManagerScrapeStatement
from processing.manager.batch.voting import BatchManagerProcessingVoting
from processing.models.tags import FakeTag


class BatchManagerMock(BatchManager[FakeTag]):
    @property
    def type_adapter_list(self):
        return TypeAdapter(List[Dict])

    @property
    def payload_s3_key_prefix(self):
        return f"test"

    @property
    def tags_per_job(self, tag=None):
        return 2


@pytest.fixture
def batch_manager_mock():
    manager = BatchManagerMock()
    manager.provider = MagicMock()
    return manager


@pytest.fixture
def batch_manager_member():
    manager = BatchManagerProcessingMember()
    manager.provider = MagicMock()
    return manager


@pytest.fixture
def batch_manager_voting():
    manager = BatchManagerProcessingVoting()
    manager.provider = MagicMock()
    return manager

@pytest.fixture
def batch_manager_group():
    manager = BatchManagerProcessingGroup()
    manager.provider = MagicMock()
    return manager


@pytest.fixture
def batch_manager_scrape_statement():
    manager = BatchManagerScrapeStatement()
    manager.provider = MagicMock()
    return manager
