from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode
from processing.pipelines.analytics import AnalyticsPipeline
from processing.pipelines.pipeline import Pipeline


class WorkerAnalytics(Worker[TermTag]):

    def _get_tags(self, term_tag: TermTag) -> List[TermTag]:
        raise NotImplementedError

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[TermTag]:
        raise NotImplementedError

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        return AnalyticsPipeline()

    def _make_payload(self, tag: TermTag) -> Dict:
        return {
            "term_tag": tag,
        }

    def _get_tags_to_process(self, payload_id: str) -> List[TermTag]:
        raise NotImplementedError

    def _save_results(self, payload: Dict):
        self.repository.save(payload["groups"])
        self.repository.save(payload["groups_members_rotation"])
        self.repository.save(payload["groups_votings_outcomes_discipline_ranking"])

        self.repository.save(payload["members"])
        self.repository.save(payload["members_voting_outcome_abstain_ranking"])
        self.repository.save(payload["members_voting_outcome_no_voted_ranking"])
        self.repository.save(payload["members_voting_outcome_rebel_ranking"])
        self.repository.save(payload["members_voting_outcome_stats"])
        self.repository.save(payload["members_voting_outcome_consistency_chamber"])
        self.repository.save(payload["members_voting_outcome_consistency_groups"])
