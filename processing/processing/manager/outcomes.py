from sqlalchemy.orm import Session

from processing.manager.batch.group import BatchManagerProcessingGroup
from processing.manager.batch.member import BatchManagerProcessingMember
from processing.manager.batch.statement import BatchManagerProcessingStatement
from processing.manager.batch.voting import BatchManagerProcessingVoting
from processing.manager.batch.legislation import BatchManagerProcessingLegislation
from processing.manager.workers.analytics import WorkerAnalytics
from processing.manager.workers.votings import WorkerVotings
from processing.manager.workers.legislation_analytics import WorkerLegislationAnalytics
from processing.manager.workers.enrichment import WorkerEnrichment
from processing.manager.workers.processing.group import WorkerProcessingGroup
from processing.manager.workers.processing.member import WorkerProcessingMember
from processing.manager.workers.processing.statement import WorkerProcessingStatement
from processing.manager.workers.processing.voting import WorkerProcessingVoting
from processing.manager.workers.processing.legislation import WorkerProcessingLegislation
from processing.models.repositories.aws.athena import AthenaRepository
from processing.models.repositories.aws.s3 import S3Repository
from processing.models.tags import TermTag, ScrapeMode
from processing.providers.aws import AwsProvider


class Manager:

    def __init__(self):
        self.repository = S3Repository()
        self.repository_athena = AthenaRepository()
        self.provider = AwsProvider()

        # TODO: Use DAO instead
        self.sqlalchemy_session = Session(self.provider.athena_engine)

        self.batch_manager_processing_member = BatchManagerProcessingMember()
        self.batch_manager_processing_voting = BatchManagerProcessingVoting()
        self.batch_manager_processing_group = BatchManagerProcessingGroup()
        self.batch_manager_processing_statement = BatchManagerProcessingStatement()
        self.batch_manager_processing_legislation = BatchManagerProcessingLegislation()

        self.worker_processing_member = WorkerProcessingMember(
            batch_manager=self.batch_manager_processing_member,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_processing_voting = WorkerProcessingVoting(
            batch_manager=self.batch_manager_processing_voting,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_processing_group = WorkerProcessingGroup(
            batch_manager=self.batch_manager_processing_group,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_processing_statement = WorkerProcessingStatement(
            batch_manager=self.batch_manager_processing_statement,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_processing_legislation = WorkerProcessingLegislation(
            batch_manager=self.batch_manager_processing_legislation,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )

        self.worker_enrichment = WorkerEnrichment(
            batch_manager=None,
            repository=self.repository,
            repository_athena=self.repository_athena,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_analytics = WorkerAnalytics(
            batch_manager=None,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_votings = WorkerVotings(
            batch_manager=None,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )
        self.worker_legislation_analytics = WorkerLegislationAnalytics(
            batch_manager=None,
            repository=self.repository,
            provider=self.provider,
            sqlalchemy_session=self.sqlalchemy_session
        )

    def set_aws_athena_result_reuse_configuration_max_age(self, value: int):
        self.provider.athena_result_reuse_configuration_max_age = value

    def save_processing_members_payload(self, payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
        self.worker_processing_member.save_payload(payload_id=payload_id, scrape_mode=scrape_mode, term_tag=term_tag)

    def save_processing_votings_payload(self, payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
        self.worker_processing_voting.save_payload(payload_id=payload_id, scrape_mode=scrape_mode, term_tag=term_tag)

    def save_processing_groups_payload(self, payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
        self.worker_processing_group.save_payload(payload_id=payload_id, scrape_mode=scrape_mode, term_tag=term_tag)

    def save_processing_statements_payload(self, payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
        self.worker_processing_statement.save_payload(payload_id=payload_id, scrape_mode=scrape_mode, term_tag=term_tag)

    def save_processing_legislation_payload(self, payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
        self.worker_processing_legislation.save_payload(
            payload_id=payload_id, scrape_mode=scrape_mode, term_tag=term_tag)

    def process_processing_member_jobs(self, payload_id):
        self.worker_processing_member.process_with_payload(payload_id=payload_id)

    def process_processing_voting_jobs(self, payload_id):
        self.worker_processing_voting.process_with_payload(payload_id=payload_id)

    def process_processing_group_jobs(self, payload_id):
        self.worker_processing_group.process_with_payload(payload_id=payload_id)

    def process_processing_statement_jobs(self, payload_id):
        self.worker_processing_statement.process_with_payload(payload_id=payload_id)

    def process_processing_legislation_jobs(self, payload_id):
        self.worker_processing_legislation.process_with_payload(payload_id=payload_id)

    def process_enrichment(self, term_tag: TermTag):
        self.worker_enrichment.set_aws_athena_result_reuse_configuration_max_age(60)  # 10 minutes
        self.worker_enrichment.process_with_term_tag(term_tag=term_tag)

    def process_analytics(self, term_tag: TermTag):
        self.worker_analytics.process_with_term_tag(term_tag=term_tag)

    def process_votings(self, term_tag: TermTag):
        self.worker_votings.process_with_term_tag(term_tag=term_tag)

    def process_legislation_analytics(self, term_tag: TermTag):
        self.worker_legislation_analytics.process_with_term_tag(term_tag=term_tag)
