import json
import os
from typing import List

from pydantic import TypeAdapter

from processing.manager.batch import BatchManager
from processing.models.tags import StatementTag, SessionDayTag


class BatchManagerScrapeStatement(BatchManager[StatementTag]):

    def tags_per_job(self, tag=None) -> int:
        return int(os.environ.get('SJ_SCRAPE_STATEMENTS_TAGS_PER_JOB', 300))

    @property
    def payload_s3_key_prefix(self):
        return "scrape/statement"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[StatementTag])

    def find_payload(self, payload_id) -> List[StatementTag]:
        tags_to_process = self.get_payload_tags_to_process(payload_id)
        tags_previously_processed = self.get_payload_previously_processed(payload_id)

        if not tags_to_process + tags_previously_processed:
            return []
        elif (tags_to_process + tags_previously_processed)[0].chamber_name in ['european-parliament']:
            tags_to_process_tmp = [tag.model_dump_json(by_alias=True, exclude={'statement_id', 'statement_id_new'}) for tag in tags_to_process]
            tags_previously_processed_tmp = [tag.model_dump_json(by_alias=True, exclude={'statement_id', 'statement_id_new'}) for tag in tags_previously_processed]

            tags_diff_tmp = list(set(tags_to_process_tmp) - set(tags_previously_processed_tmp))
            # Tags were dumped without statement ids to dedup at session-day level.
            # Restore the scraper's session-day placeholder so the tag re-validates.
            tags_diff = [StatementTag.model_validate({**json.loads(tag), 'statementId': '-'}) for tag in tags_diff_tmp]

            return tags_diff

        return list(set(tags_to_process) - set(tags_previously_processed))


class BatchManagerProcessingStatement(BatchManager[StatementTag]):

    def tags_per_job(self, tag=None) -> int:
        if tag and tag.chamber_name in ['sejm', 'senat']:
            return int(os.environ.get('SJ_PROCESSING_STATEMENTS_TAGS_PER_JOB', 1))

        return int(os.environ.get('SJ_PROCESSING_STATEMENTS_TAGS_PER_JOB', 100))

    @property
    def payload_s3_key_prefix(self):
        return "processing/statement"

    @property
    def type_adapter_list(self):
        return TypeAdapter(List[StatementTag])

    def find_payload(self, payload_id) -> List[StatementTag]:
        tags_to_process = self.get_payload_tags_to_process(payload_id)
        tags_previously_processed = self.get_payload_previously_processed(payload_id)

        tags_diff = list(set(tags_to_process) - set(tags_previously_processed))

        if tags_diff and tags_diff[0].chamber_name in ['sejm', 'senat']:
            session_day_tags_to_process = [
                SessionDayTag(
                    chamberName=tag.chamber_name, termId=tag.term_id, sessionId=tag.session_id, dateId=tag.date_id)
                for tag in tags_to_process
            ]
            session_day_tags_previously_processed = [
                SessionDayTag(
                    chamberName=tag.chamber_name, termId=tag.term_id, sessionId=tag.session_id, dateId=tag.date_id)
                for tag in tags_previously_processed
            ]

            session_day_tags_diff = list(set(session_day_tags_to_process) - set(session_day_tags_previously_processed))

            # Timeline is built base on statement with statement_id == 0
            # So we only need tags with statement_id == 0
            tags = [
                StatementTag(
                    chamberName=session_day_tag.chamber_name,
                    termId=session_day_tag.term_id,
                    sessionId=session_day_tag.session_id,
                    dateId=session_day_tag.date_id,
                    statementId='0'
                )
                for session_day_tag in session_day_tags_diff
            ]
            return list(set(tags))

        return tags_diff
