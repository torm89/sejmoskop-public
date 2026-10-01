import os
from typing import List

from pydantic import TypeAdapter

from processing.manager.batch import BatchManager
from processing.models.tags import GroupTag


class BatchManagerScrapeGroup(BatchManager[GroupTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_SCRAPE_GROUPS_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "scrape/group"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[GroupTag])


class BatchManagerProcessingGroup(BatchManager[GroupTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_PROCESSING_GROUPS_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "processing/group"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[GroupTag])
