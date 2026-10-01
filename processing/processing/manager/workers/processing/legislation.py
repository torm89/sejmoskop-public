from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode, LegislationTag
from processing.pipelines.pipeline import Pipeline
from processing.pipelines.processing.sejm.legislation import LegislationProcessingPipelineSejm


class WorkerProcessingLegislation(Worker[LegislationTag]):

    def _get_tags(self, term_tag: TermTag) -> List[LegislationTag]:
        return self.repository.list_legislation_hot_data(term_tag=term_tag)

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[LegislationTag]:
        # Legislation is mutable (stages accrue over time), so we always
        # re-process every item — no "previously processed" skip list.
        return []

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        if term.chamber_name == 'sejm':
            return LegislationProcessingPipelineSejm()

        super()._pipeline_factory(term=term)

    def _make_payload(self, tag: LegislationTag) -> Dict:
        return {
            "legislation_tag": tag,
            "legislation_data": self.repository.fetch_legislation_hot_data(tag=tag)
        }

    def _save_results(self, payload: Dict):
        self.repository.save(payload["legislation_data"])
        self.repository.save(payload["legislation_stage_data"]) if payload["legislation_stage_data"] else None
        self.repository.save(payload["legislation_voting_data"]) if payload["legislation_voting_data"] else None
