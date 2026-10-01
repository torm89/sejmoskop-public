import json
import re
from typing import Dict, Type

from processing.models.dao import D
from processing.models.dao.aws.s3.preprocessing import PreprocessingDaoAwsS3, PreprocessingHotDaoAwsS3
from processing.models.data.preprocessing.member import MemberData, MemberImageData
from processing.models.tags import MemberTag, TermTag
from botocore.exceptions import ClientError


class MemberHotDaoAwsS3(PreprocessingHotDaoAwsS3[MemberTag, Dict]):

    @staticmethod
    def s3_key(tag: MemberTag) -> str:
        return f'{tag.chamber_name}/{tag.term_id}/members/{tag.member_id}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'{term_tag.chamber_name}/{term_tag.term_id}/members/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> MemberTag:
        r = re.search(r'^(?P<chamberName>[\w-]+)/(?P<termId>\w+)/members/(?P<memberId>\d+)\.json$', key)
        return MemberTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            memberId=r.group('memberId')
        )

    def get(self, tag: MemberTag) -> Dict:
        return json.loads(self.fetch_s3_object(tag=tag))

    def save(self, data: D) -> None:
        raise NotImplementedError


class MemberDaoAwsS3(PreprocessingDaoAwsS3[MemberTag, MemberData]):

    @staticmethod
    def s3_key(tag: MemberTag) -> str:
        return f'tables/members/chamber_name={tag.chamber_name}/term_id={tag.term_id}/{tag.member_id}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'tables/members/chamber_name={term_tag.chamber_name}/term_id={term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> MemberTag:
        r = re.search(
            r'^tables/members/chamber_name=(?P<chamberName>[\w-]+)/term_id=(?P<termId>\w+)/(?P<memberId>\d+)\.json$', key)
        return MemberTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            memberId=r.group('memberId')
        )

    def get(self, tag: MemberTag) -> MemberData:
        raise NotImplementedError


class MemberImageDaoAwsS3(PreprocessingDaoAwsS3[MemberTag, MemberImageData]):

    @staticmethod
    def s3_key(tag: MemberTag) -> str:
        return f"images/members/{tag.chamber_name}/{tag.term_id}/{tag.member_id}.jpg"

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'images/members/{term_tag.chamber_name}/{term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> MemberTag:
        r = re.search(r'^images/members/(?P<chamberName>[\w-]+)/(?P<termId>\w+)/(?P<memberId>\d+)\.jpg$', key)
        return MemberTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            memberId=r.group('memberId')
        )

    def get(self, tag: MemberTag) -> MemberImageData:
        data = None
        try:
            data = self.provider.s3_get_object(bucket_name=self.bucket_name, key=self.s3_key(tag=tag))
        except ClientError as error:
            if error.response['Error']['Code'] != 'NoSuchKey':
                raise error

        return MemberImageData(tag=tag, data=data)

    def save(self, data: MemberImageData) -> None:
        self.provider.s3_save_object(bucket_name=self.bucket_name, key=self.s3_key(tag=data.tag), data=data.data)
