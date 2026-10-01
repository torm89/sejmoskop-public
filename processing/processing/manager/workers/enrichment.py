from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.tags import TermTag, ScrapeMode
from processing.pipelines.enrichment import EnrichmentPipelineSejm, EnrichmentPipelineSenat, \
    EnrichmentPipelineEuropeanParliament
from processing.pipelines.pipeline import Pipeline


class WorkerEnrichment(Worker[TermTag]):

    def _get_tags(self, term_tag: TermTag) -> List[TermTag]:
        raise NotImplementedError

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[TermTag]:
        raise NotImplementedError

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        if term.chamber_name == 'sejm':
            return EnrichmentPipelineSejm()
        elif term.chamber_name == 'senat':
            return EnrichmentPipelineSenat()
        elif term.chamber_name == 'european-parliament':
            return EnrichmentPipelineEuropeanParliament()

        return super()._pipeline_factory(term=term)

    def _make_payload(self, tag: TermTag) -> Dict:
        return {
            "term_tag": tag,
        }

    def _get_tags_to_process(self, payload_id: str) -> List[TermTag]:
        raise NotImplementedError

    def _save_results(self, payload: Dict):
        # There is noting to save for this worker
        pass
