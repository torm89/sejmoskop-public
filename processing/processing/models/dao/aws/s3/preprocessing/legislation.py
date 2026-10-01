import json
import re
from typing import Dict, Type

from processing.models.dao.aws.s3.preprocessing import PreprocessingDaoAwsS3, PreprocessingHotDaoAwsS3
from processing.models.data.preprocessing.legislation import LegislationData, LegislationStageData, \
    LegislationVotingData
from processing.models.tags import LegislationTag, TermTag


class LegislationHotDaoAwsS3(PreprocessingHotDaoAwsS3[LegislationTag, Dict]):

    @staticmethod
    def s3_key(tag: LegislationTag) -> str:
        return f'{tag.chamber_name}/{tag.term_id}/legislation/{tag.legislation_number}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'{term_tag.chamber_name}/{term_tag.term_id}/legislation/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> LegislationTag:
        r = re.search(
            r'^(?P<chamberName>[\w-]+)/(?P<termId>\w+)/legislation/(?P<legislationNumber>[^/]+)\.json$', key)
        return LegislationTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            legislationNumber=r.group('legislationNumber')
        )

    def get(self, tag: LegislationTag) -> Dict:
        return json.loads(self.fetch_s3_object(tag=tag))

    def save(self, data: Dict) -> None:
        raise NotImplementedError


class LegislationDaoAwsS3(PreprocessingDaoAwsS3[LegislationTag, LegislationData]):

    @staticmethod
    def s3_key(tag: LegislationTag) -> str:
        return f'tables/legislation/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.legislation_number}.csv'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/legislation/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> LegislationTag:
        r = re.search(
            r'^tables/legislation/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<legislationNumber>[^/]+)\.csv$',
            key
        )
        return LegislationTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            legislationNumber=r.group('legislationNumber')
        )

    def get(self, tag: LegislationTag) -> LegislationData:
        return LegislationData.from_csv(tag=tag, data=self.fetch_s3_object(tag=tag))


class LegislationStageDaoAwsS3(PreprocessingDaoAwsS3[LegislationTag, LegislationStageData]):

    @staticmethod
    def s3_key(tag: LegislationTag) -> str:
        return f'tables/legislation_stages/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.legislation_number}.csv'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/legislation_stages/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> LegislationTag:
        r = re.search(
            r'^tables/legislation_stages/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<legislationNumber>[^/]+)\.csv$',
            key
        )
        return LegislationTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            legislationNumber=r.group('legislationNumber')
        )

    def get(self, tag: LegislationTag) -> LegislationStageData:
        return LegislationStageData.from_csv(tag=tag, data=self.fetch_s3_object(tag=tag))


class LegislationVotingDaoAwsS3(PreprocessingDaoAwsS3[LegislationTag, LegislationVotingData]):

    @staticmethod
    def s3_key(tag: LegislationTag) -> str:
        return f'tables/legislation_votings/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.legislation_number}.csv'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/legislation_votings/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> LegislationTag:
        r = re.search(
            r'^tables/legislation_votings/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<legislationNumber>[^/]+)\.csv$',
            key
        )
        return LegislationTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            legislationNumber=r.group('legislationNumber')
        )

    def get(self, tag: LegislationTag) -> LegislationVotingData:
        return LegislationVotingData.from_csv(tag=tag, data=self.fetch_s3_object(tag=tag))
