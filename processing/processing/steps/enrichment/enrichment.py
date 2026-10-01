import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Generic, TypeVar, List, Dict

from processing.models.tags import VotingTag, VotingOutcomeTag, MemberTag, GroupTag, StatementTag, TermTag
from processing.steps.step import Step

T = TypeVar('T', MemberTag, VotingTag, GroupTag, StatementTag)


class EnrichmentStep(Step, ABC, Generic[T]):

    @classmethod
    def timedelta(cls) -> timedelta:
        return timedelta(days=1)

    @classmethod
    def younger_than_date(cls) -> datetime:
        return datetime.utcnow().replace(tzinfo=timezone.utc) - cls.timedelta()

    @classmethod
    @abstractmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[T]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _step_make_payload(cls, tag: T, *args, **kwargs) -> Dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _step_run(cls, payload, *args, **kwargs) -> Dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _step_save_payload(cls, payload, *args, **kwargs):
        raise NotImplementedError

    # TODO: _step_* methods should be outside of the class, likely in a worker class.
    #       Split payload to payload and ste_payload
    @classmethod
    def run(cls, payload, *args, **kwargs):
        term_tag = payload['term_tag']

        tags = cls._step_tags(term_tag, *args, **kwargs)

        total = len(tags)
        log_every = max(1, total // 10)
        for i, tag in enumerate(tags):
            if i % log_every == 0 or i == total - 1:
                logging.info(f'-- enrichment -- {(i + 1) / total * 100:.2f}% -- {tag.model_dump_json()}\t -- {cls}')

            step_payload = cls._step_make_payload(tag, *args, **kwargs)
            step_payload.update(cls._step_run(step_payload, *args, **kwargs))
            cls._step_save_payload(step_payload, *args, **kwargs)

        return payload


class EnrichmentTermStep(EnrichmentStep[TermTag], ABC):
    @classmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[TermTag]:
        return [term_tag]


class EnrichmentMembersStep(EnrichmentStep[MemberTag], ABC):
    @classmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[MemberTag]:
        repository = kwargs['repository']

        return repository.list_member_data_younger_than(term_tag=term_tag, date=cls.younger_than_date())


class EnrichmentGroupsStep(EnrichmentStep[GroupTag], ABC):
    @classmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[GroupTag]:
        repository = kwargs['repository']

        return repository.list_group_data_younger_than(term_tag=term_tag, date=cls.younger_than_date())


class EnrichmentVotingsStep(EnrichmentStep[VotingTag], ABC):
    @classmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[VotingTag]:
        repository = kwargs['repository']

        return repository.list_voting_data_younger_than(term_tag=term_tag, date=cls.younger_than_date())


class EnrichmentVotingOutcomesStep(EnrichmentStep[VotingOutcomeTag], ABC):
    @classmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[VotingOutcomeTag]:
        repository = kwargs['repository']

        return repository.list_voting_outcome_data_younger_than(term_tag=term_tag, date=cls.younger_than_date())


class EnrichmentStatementsStep(EnrichmentStep[StatementTag], ABC):
    @classmethod
    def _step_tags(cls, term_tag: TermTag, *args, **kwargs) -> List[StatementTag]:
        repository = kwargs['repository']

        return repository.list_statement_data_younger_than(term_tag=term_tag, date=cls.younger_than_date())
