import os
from typing import List

from pydantic import TypeAdapter

from processing.manager.batch import BatchManager
from processing.models.tags import LegislationTag


class BatchManagerScrapeLegislation(BatchManager[LegislationTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_SCRAPE_LEGISLATION_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "scrape/legislation"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[LegislationTag])


class BatchManagerProcessingLegislation(BatchManager[LegislationTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_PROCESSING_LEGISLATION_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "processing/legislation"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[LegislationTag])
