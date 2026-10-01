from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode, GroupTag
from processing.pipelines.pipeline import Pipeline
from processing.pipelines.processing.european.parliament.group import GroupProcessingPipelineEuropeanParliament
from processing.pipelines.processing.sejm.group import GroupProcessingPipelineSejm
from processing.pipelines.processing.senat.group import GroupProcessingPipelineSenat


class WorkerProcessingGroup(Worker[GroupTag]):

    def _get_tags(self, term_tag: TermTag) -> List[GroupTag]:
        return self.repository.list_group_hot_data(term_tag=term_tag)

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[GroupTag]:
        return self.repository.list_group_data(term_tag=term_tag) if scrape_mode == "new" else []

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        if term.chamber_name == 'sejm':
            return GroupProcessingPipelineSejm()
        elif term.chamber_name == 'senat':
            return GroupProcessingPipelineSenat()
        elif term.chamber_name == 'european-parliament':
            return GroupProcessingPipelineEuropeanParliament()

        super()._pipeline_factory(term=term)

    def _make_payload(self, tag: GroupTag) -> Dict:
        return {
            "group_tag": tag,
            "group_data": self.repository.fetch_group_hot_data(tag=tag)
        }

    def _save_results(self, payload: Dict):
        self.repository.save(payload["group_data"])
