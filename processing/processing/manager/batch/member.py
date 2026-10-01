import os
from typing import List

from pydantic import TypeAdapter

from processing.manager.batch import BatchManager
from processing.models.tags import MemberTag


class BatchManagerScrapeMember(BatchManager[MemberTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_SCRAPE_MEMBERS_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "scrape/member"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[MemberTag])


class BatchManagerProcessingMember(BatchManager[MemberTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_PROCESSING_MEMBERS_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "processing/member"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[MemberTag])
