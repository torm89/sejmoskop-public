from typing import List, Dict

from processing.manager.workers import Worker
from processing.models.data.preprocessing.statement import StatementData
from processing.models.tags import TermTag, ScrapeMode, StatementTag
from processing.pipelines.pipeline import Pipeline
from processing.pipelines.processing.european.parliament.statement import StatementProcessingPipelineEuropeanParliament
from processing.pipelines.processing.sejm.statement import StatementProcessingPipelineSejm
from processing.pipelines.processing.senat.statement import StatementProcessingPipelineSenat


class WorkerProcessingStatement(Worker[StatementTag]):

    def _get_tags(self, term_tag: TermTag) -> List[StatementTag]:
        return self.repository.list_statement_hot_data(term_tag=term_tag)

    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[StatementTag]:
        return self.repository.list_statement_data(term_tag=term_tag) if scrape_mode == "new" else []

    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        if term.chamber_name == 'sejm':
            return StatementProcessingPipelineSejm()
        elif term.chamber_name == 'senat':
            return StatementProcessingPipelineSenat()
        elif term.chamber_name == 'european-parliament':
            return StatementProcessingPipelineEuropeanParliament()

        return super()._pipeline_factory(term=term)

    def _make_payload(self, tag: StatementTag) -> Dict:
        if tag.chamber_name in ['sejm', 'senat']:
            return {
                "statement_tag": tag,
                "statement_proceedings": self.repository.fetch_statement_hot_data(tag=tag),
                "statement_dao": self.repository.statement_hot_dao_aws_s3
            }

        return {
            "statement_tag": tag,
            "statement_data": self.repository.fetch_statement_hot_data(tag=tag)
        }

    def _save_results(self, payload: Dict):
        if payload["statement_tag"].chamber_name in ['sejm', 'senat']:
            self.repository.bulk_save(payload["statements_data_list"])
        else:
            statement_tag = payload["statement_tag"]
            statement_data = payload["statement_data"]

            self.repository.save(StatementData.from_dict(tag=statement_tag, data=statement_data))
