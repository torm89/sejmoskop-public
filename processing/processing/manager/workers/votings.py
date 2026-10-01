from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode
from processing.pipelines.pipeline import Pipeline
from processing.pipelines.votings import VotingsPipeline


class WorkerVotings(Worker[TermTag]):

    def _get_tags(self, term_tag: TermTag) -> List[TermTag]:
        raise NotImplementedError

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[TermTag]:
        raise NotImplementedError

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        return VotingsPipeline()

    def _make_payload(self, tag: TermTag) -> Dict:
        return {
            "term_tag": tag,
        }

    def _get_tags_to_process(self, payload_id: str) -> List[TermTag]:
        raise NotImplementedError

    def _save_results(self, payload: Dict):
        self.repository.save(payload["voting_roll_call"])
