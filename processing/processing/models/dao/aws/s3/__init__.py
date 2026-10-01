import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from botocore.exceptions import ClientError as BotoClientError

from processing.models.dao import Dao, D, T
from processing.models.tags import TermTag
from processing.providers.aws import AwsProvider


class DaoAwsS3(Dao[T, D], ABC):

    def __init__(self):
        self.provider = AwsProvider()

    @property
    @abstractmethod
    def bucket_name(self) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def s3_key(tag: T) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def s3_prefix(term_tag: TermTag) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def tag_from_s3_key(key=str) -> T:
        raise NotImplementedError

    def list(self, term_tag: TermTag) -> List[T]:
        objs = self.provider.s3_list_objects(bucket_name=self.bucket_name, prefix=self.s3_prefix(term_tag=term_tag))
        return [self.tag_from_s3_key(obj.get("Key")) for obj in objs]

    def list_younger_than(self, term_tag: TermTag, date: datetime) -> List[T]:
        objs = self.provider.s3_list_objects(bucket_name=self.bucket_name, prefix=self.s3_prefix(term_tag=term_tag))
        return [self.tag_from_s3_key(obj.get("Key")) for obj in objs if obj.get("LastModified") > date]

    def fetch_s3_object(self, tag: T) -> str:
        try:
            return self.provider.s3_get_object(bucket_name=self.bucket_name, key=self.s3_key(tag=tag))
        except BotoClientError as e:
            logging.error(
                f"Boto client error: {e.response['Error']['Code']} - bucket: {self.bucket_name} - key: {self.s3_key(tag=tag)}")
            raise e

    async def fetch_s3_object_async(self, tag: T) -> str:
        return await self.provider.s3_get_object_async(bucket_name=self.bucket_name, key=self.s3_key(tag=tag))

    @abstractmethod
    def save(self, data: D) -> None:
        self.provider.s3_save_object(
            bucket_name=self.bucket_name, key=self.s3_key(tag=data.tag), data=data.to_file_bytes())
