from datetime import datetime, timedelta, timezone
from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode, MemberTag
from processing.pipelines.pipeline import Pipeline
from processing.pipelines.processing.european.parliament.member import MemberProcessingPipelineEuropeanParliament
from processing.pipelines.processing.sejm.member import MemberProcessingPipelineSejm
from processing.pipelines.processing.senat.member import MemberProcessingPipelineSenat


class WorkerProcessingMember(Worker[MemberTag]):

    def _get_tags(self, term_tag: TermTag) -> List[MemberTag]:
        return self.repository.list_member_hot_data(term_tag=term_tag)

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[MemberTag]:
        date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=1)
        return self.repository.list_member_data_younger_than(term_tag=term_tag, date=date) if scrape_mode == "new" else []

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        if term.chamber_name == 'sejm':
            return MemberProcessingPipelineSejm()
        elif term.chamber_name == 'senat':
            return MemberProcessingPipelineSenat()
        elif term.chamber_name == 'european-parliament':
            return MemberProcessingPipelineEuropeanParliament()

        super()._pipeline_factory(term=term)

    def _make_payload(self, tag: MemberTag) -> Dict:
        return {
            "member_tag": tag,
            "member_data": self.repository.fetch_member_hot_data(tag=tag),
            "member_current_image": self.repository.fetch_member_image(tag=tag)
        }

    def _save_results(self, payload: Dict):
        self.repository.save(payload["member_data"])
        self.repository.save(payload["member_image"])
