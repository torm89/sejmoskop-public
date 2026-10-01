import json
import re
from typing import Dict, Type

from processing.models.dao import D
from processing.models.dao.aws.s3.preprocessing import PreprocessingDaoAwsS3, PreprocessingHotDaoAwsS3
from processing.models.data.preprocessing.group import GroupData, GroupImageData
from processing.models.tags import GroupTag, TermTag


class GroupHotDaoAwsS3(PreprocessingHotDaoAwsS3[GroupTag, Dict]):
    @staticmethod
    def s3_key(tag: GroupTag) -> str:
        return f'{tag.chamber_name}/{tag.term_id}/groups/{tag.name}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'{term_tag.chamber_name}/{term_tag.term_id}/groups/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> GroupTag:
        r = re.search(r'^(?P<chamberName>[\w-]+)/(?P<termId>\w+)/groups/(?P<name>.+)\.json$', key)
        return GroupTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            name=r.group('name')
        )

    def get(self, tag: GroupTag) -> Dict:
        return json.loads(self.fetch_s3_object(tag=tag))

    def save(self, data: D) -> None:
        raise NotImplementedError


class GroupDaoAwsS3(PreprocessingDaoAwsS3[GroupTag, GroupData]):

    @staticmethod
    def s3_key(tag: GroupTag) -> str:
        return f'tables/groups/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.name}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/groups/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> GroupTag:
        r = re.search(
            r'^tables/groups/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<name>.+)\.json$', key)
        return GroupTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            name=r.group('name')
        )

    def get(self, tag: GroupTag) -> GroupData:
        raise NotImplementedError


class GroupImageDaoAwsS3(PreprocessingDaoAwsS3[GroupTag, GroupImageData]):

    @staticmethod
    def s3_key(tag: GroupTag) -> str:
        return f"images/groups/{tag.chamber_name}/{tag.term_id}/{tag.name}.jpg"

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'images/groups/{term_tag.chamber_name}/{term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> GroupTag:
        r = re.search(r'^images/groups/(?P<chamberName>[\w-]+)/(?P<termId>\w+)/(?P<name>.+)\.jpg$', key)
        return GroupTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            name=r.group('name')
        )

    def get(self, tag: GroupTag) -> GroupImageData:
        raise NotImplementedError

    def save(self, data: GroupImageData) -> None:
        self.provider.s3_save_object(bucket_name=self.bucket_name, key=self.s3_key(tag=data.tag), data=data.data)
