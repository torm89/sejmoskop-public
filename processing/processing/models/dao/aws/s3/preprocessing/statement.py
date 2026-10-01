import asyncio
import json
import re
from typing import Dict, Type, List

from processing.models.dao import D
from processing.models.dao.aws.s3.preprocessing import PreprocessingHotDaoAwsS3, PreprocessingDaoAwsS3
from processing.models.data.preprocessing.statement import StatementData
from processing.models.tags import StatementTag, TermTag
from processing.utils.exceptions import SaveDataException


class StatementHotDaoAwsS3(PreprocessingHotDaoAwsS3[StatementTag, Dict]):

    @staticmethod
    def s3_key(tag: StatementTag) -> str:
        return f'{tag.chamber_name}/{tag.term_id}/statements/{tag.session_id}/{tag.date_id}/{tag.statement_id}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'{term_tag.chamber_name}/{term_tag.term_id}/statements/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> StatementTag:
        r = re.search(
            r'^(?P<chamberName>[\w-]+)/(?P<termId>\w+)/statements/(?P<sessionId>\w+)/(?P<dateId>[\w-]+)/(?P<statementId>.+)\.json$',
            key)
        return StatementTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            sessionId=r.group('sessionId'),
            dateId=r.group('dateId'),
            statementId=r.group('statementId')
        )

    def get(self, tag: StatementTag) -> Dict:
        return json.loads(self.fetch_s3_object(tag=tag))

    async def get_async(self, tag: StatementTag) -> Dict:
        return json.loads(await self.fetch_s3_object_async(tag=tag))

    def save(self, data: Dict) -> None:
        raise NotImplementedError


class StatementDaoAwsS3(PreprocessingDaoAwsS3[StatementTag, StatementData]):

    @staticmethod
    def s3_key(tag: StatementTag) -> str:
        if tag.chamber_name in ['sejm', 'senat']:
            return f'opensearch/statements/{tag.chamber_name}/{tag.term_id}/{tag.session_id}/{tag.date_id}/{tag.statement_id_new}.json'
        return f'opensearch/statements/{tag.chamber_name}/{tag.term_id}/{tag.session_id}/{tag.date_id}/{tag.statement_id}.json'

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        return f'opensearch/statements/{term_tag.chamber_name}/{term_tag.term_id}/'

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> StatementTag:
        r = re.search(
            r'^opensearch/statements/(?P<chamberName>[\w-]+)/(?P<termId>\w+)/(?P<sessionId>\w+)/(?P<dateId>[\w-]+)/(?P<statementIdNew>[\w.-]+)\.json$',
            key
        )
        # TODO: This is a temporary fix for the issue with the statement_id_new field
        chamber_name = r.group('chamberName')
        if chamber_name in ['sejm', 'senat']:
            return StatementTag(
                chamberName=chamber_name,
                termId=r.group('termId'),
                sessionId=r.group('sessionId'),
                dateId=r.group('dateId'),
                statementIdNew=int(r.group('statementIdNew'))
            )

        return StatementTag(
            chamberName=r.group('chamberName'),
            termId=r.group('termId'),
            sessionId=r.group('sessionId'),
            dateId=r.group('dateId'),
            statementId=r.group('statementIdNew')
        )

    def get(self, tag: StatementTag) -> StatementData:
        return StatementData(tag=tag, data=json.loads(self.fetch_s3_object(tag=tag)))

    def save(self, data: D) -> None:
        if data.tag.statement_id_new == -1:
            raise SaveDataException('Empty statement_id_new is not allowed')

        self.provider.s3_save_object(
            bucket_name=self.bucket_name,
            key=self.s3_key(tag=data.tag),
            data=json.dumps(data.data, indent=2).encode('utf-8')
        )

    def bulk_save(self, data: List[D]) -> None:
        for obj in data:
            if obj.tag.statement_id_new == -1:
                raise SaveDataException(f'Empty statement_id_new is not allowed {obj.tag}')

        objs = [
            {
                "bucket_name": self.bucket_name,
                "key": self.s3_key(tag=obj.tag),
                "data": json.dumps(obj.data, indent=2).encode('utf-8')
            }
            for obj in data
        ]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.provider.s3_save_objects_bulk(objs=objs))
