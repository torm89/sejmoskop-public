from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode, VotingTag
from processing.pipelines.pipeline import Pipeline
from processing.pipelines.processing.european.parliament.voting import VotingProcessingPipelineEuropeanParliament
from processing.pipelines.processing.sejm.voting import VotingProcessingPipelineSejm
from processing.pipelines.processing.senat.voting import VotingProcessingPipelineSenat


class WorkerProcessingVoting(Worker[VotingTag]):

    def _get_tags(self, term_tag: TermTag) -> List[VotingTag]:
        return self.repository.list_voting_hot_data(term_tag=term_tag)

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[VotingTag]:
        return self.repository.list_voting_data(term_tag=term_tag) if scrape_mode == "new" else []

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        if term.chamber_name == 'sejm':
            return VotingProcessingPipelineSejm()
        elif term.chamber_name == 'senat':
            return VotingProcessingPipelineSenat()
        elif term.chamber_name == 'european-parliament':
            return VotingProcessingPipelineEuropeanParliament()

        super()._pipeline_factory(term=term)

    def _make_payload(self, tag: VotingTag) -> Dict:
        return {
            "voting_tag": tag,
            "voting_data": self.repository.fetch_voting_hot_data(tag=tag)
        }

    def _save_results(self, payload: Dict):
        self.repository.save(payload["voting_data"])
        self.repository.save(payload["voting_outcome_data"]) if payload["voting_outcome_data"] else None
