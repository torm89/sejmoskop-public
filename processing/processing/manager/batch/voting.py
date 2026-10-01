import os
from typing import List

from pydantic import TypeAdapter

from processing.manager.batch import BatchManager
from processing.models.tags import VotingTag


class BatchManagerScrapeVoting(BatchManager[VotingTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_SCRAPE_VOTINGS_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "scrape/voting"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[VotingTag])

    def get_payload_tags_to_process(self, payload_id) -> List[VotingTag]:
        """Temporary fix for European Parliament voting tags with date 2023-07-11"""
        # TODO: Remove this
        tags = super().get_payload_tags_to_process(payload_id)

        return [tag for tag in tags if tag.date != '2023-07-11']


class BatchManagerProcessingVoting(BatchManager[VotingTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_PROCESSING_VOTINGS_TAGS_PER_JOB', 250))

    @property
    def payload_s3_key_prefix(self):
        return "processing/voting"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[VotingTag])
