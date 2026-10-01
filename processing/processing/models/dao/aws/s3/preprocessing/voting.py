import json
import re
from typing import Dict, Type

from processing.models.dao.aws.s3.preprocessing import PreprocessingDaoAwsS3, PreprocessingHotDaoAwsS3
from processing.models.data.preprocessing.voting import VotingData, VotingOutcomeData
from processing.models.tags import VotingTag, TermTag, VotingOutcomeTag


class VotingHotDaoAwsS3(PreprocessingHotDaoAwsS3[VotingTag, Dict]):

    @staticmethod
    def s3_key(tag: VotingTag) -> str:
        return f'{tag.chamber_name}/{tag.term_id}/votings/{tag.session_id}/{tag.voting_id}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'{term_tag.chamber_name}/{term_tag.term_id}/votings/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> VotingTag:
        r = re.search(r'^(?P<chamberName>[\w-]+)/(?P<termId>\w+)/votings/(?P<sessionId>\w+)/(?P<votingId>[\w,]+)\.json$', key)
        return VotingTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            sessionId=r.group('sessionId'),
            votingId=r.group('votingId')
        )

    def get(self, tag: VotingTag) -> Dict:
        return json.loads(self.fetch_s3_object(tag=tag))

    def save(self, data: Dict) -> None:
        raise NotImplementedError


class VotingDaoAwsS3(PreprocessingDaoAwsS3[VotingTag, VotingData]):

    @staticmethod
    def s3_key(tag: VotingTag) -> str:
        return f'tables/votings/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.session_id}/{tag.voting_id}.csv'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/votings/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> VotingTag:
        r = re.search(
            r'^tables/votings/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<sessionId>\w+)/(?P<votingId>[\w,]+)\.csv$',
            key
        )
        return VotingTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            sessionId=r.group('sessionId'),
            votingId=r.group('votingId')
        )

    def get(self, tag: VotingTag) -> VotingData:
        return VotingData.from_csv(tag=tag, data=self.fetch_s3_object(tag=tag))


class VotingOutcomeDaoAwsS3(PreprocessingDaoAwsS3[VotingTag, VotingOutcomeData]):

    @staticmethod
    def s3_key(tag: VotingTag) -> str:
        return f"tables/votings_outcomes/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.session_id}/{tag.voting_id}.csv"

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/votings_outcomes/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> VotingOutcomeTag:
        r = re.search(
            r'^tables/votings_outcomes/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<sessionId>\w+)/(?P<votingId>[\w,]+)\.csv$',
            key
        )
        return VotingOutcomeTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            sessionId=r.group('sessionId'),
            votingId=r.group('votingId'),
        )

    def get(self, tag: VotingOutcomeTag) -> VotingOutcomeData:
        return VotingOutcomeData.from_csv(tag=tag, data=self.fetch_s3_object(tag=tag))
