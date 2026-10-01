import logging
from abc import abstractmethod, ABC
from typing import Generic, List, Dict, Union

from sqlalchemy.orm import Session

from processing.manager.batch import BatchManager
from processing.models.dao import D, T
from processing.models.repositories.aws.athena import AthenaRepository
from processing.models.repositories.aws.s3 import S3Repository
from processing.models.tags import TermTag, ScrapeMode
from processing.pipelines.pipeline import Pipeline
from processing.providers.aws import AwsProvider
from processing.utils.exceptions import PipelineNotImplementedError


class Worker(Generic[T], ABC):

    def __init__(
            self, batch_manager: BatchManager, repository: S3Repository, provider: AwsProvider,
            sqlalchemy_session: Session, repository_athena: AthenaRepository = None
    ):
        self.batch_manager = batch_manager
        self.repository = repository
        self.repository_athena = repository_athena
        self.provider = provider

        self.sqlalchemy_session = sqlalchemy_session

    def set_aws_athena_result_reuse_configuration_max_age(self, value: int):
        self.provider.athena_result_reuse_configuration_max_age = value

    @abstractmethod
    def _get_tags(self, term_tag: TermTag) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def _get_tags_previously_processed(self, term_tag: TermTag, scrape_mode: ScrapeMode) -> List[T]:
        raise NotImplementedError

    def save_payload(self, payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
        tags = self._get_tags(term_tag=term_tag)
        tags_previously_processed = self._get_tags_previously_processed(term_tag=term_tag, scrape_mode=scrape_mode)

        logging.info(
            f"-- save_processing_payload \t -- tags: {len(tags)} -- tags_previously_processed: {len(tags_previously_processed)}")

        self.batch_manager.save_payload_tags_to_process(tags=tags, payload_id=payload_id)
        self.batch_manager.save_payload_tags_previously_processed(
            tags=tags_previously_processed, payload_id=payload_id)

    @abstractmethod
    def _pipeline_factory(self, term: TermTag) -> Pipeline:
        raise PipelineNotImplementedError(f"Pipeline for term {term} not implemented")

    @abstractmethod
    def _make_payload(self, tag: Union[T, TermTag]) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def _save_results(self, payload: Dict):
        raise NotImplementedError

    def _get_tags_to_process(self, payload_id: str) -> List[T]:
        return self.batch_manager.get_tags_from_payload(payload_id=payload_id)

    def process_with_payload(self, payload_id):
        tags = self._get_tags_to_process(payload_id=payload_id)
        total_tags = len(tags)

        for i, tag in enumerate(tags, start=1):
            percentage = (i / total_tags) * 100
            logging.info(
                f'-- processing -- {i:3d}/{total_tags} ({percentage:6.2f}%) --  {tag.model_dump_json()}')

            pipeline = self._pipeline_factory(term=tag)

            payload = self._make_payload(tag=tag)
            payload = pipeline.run(payload=payload, session=self.sqlalchemy_session)

            self._save_results(payload)

    def process_with_term_tag(self, term_tag: TermTag):
        logging.info(
            f'-- processing -- \t\t\t --  {term_tag.model_dump_json()}')

        pipeline = self._pipeline_factory(term=term_tag)

        payload = self._make_payload(tag=term_tag)
        payload = pipeline.run(
            payload=payload, repository=self.repository, session=self.sqlalchemy_session, provider=self.provider,
            repository_athena=self.repository_athena
        )

        self._save_results(payload)
