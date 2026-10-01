import asyncio
import os
from abc import ABC, abstractmethod
from typing import Type, List

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from processing.models.dao import D, T
from processing.models.dao.aws.s3 import DaoAwsS3
from processing.models.data import Data
from processing.models.tags import TermTag


class TagsAnalyticsDaoAwsS3(DaoAwsS3[T, D], ABC):

    @property
    def bucket_name(self) -> str:
        return os.environ.get('AWS_S3_DATA_BUCKET_NAME')

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        raise NotImplementedError

    @staticmethod
    def tag_from_s3_key(key=Type[str]) -> TermTag:
        raise NotImplementedError

    def get(self, tag: T) -> D:
        raise NotImplementedError

    def save(self, data: D) -> None:
        self.provider.s3_save_object(
            bucket_name=self.bucket_name,
            key=self.s3_key(tag=data.tag),
            data=data.df_json().encode('utf-8')
        )


class TagAnalyticsDaoAwsS3(TagsAnalyticsDaoAwsS3[T, D], ABC):

    @staticmethod
    def s3_key(tag: T) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def s3_key_by(tag: T, by: List[str]) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def by_column_name(self) -> List[str]:
        raise NotImplementedError

    def group_by(self, data: D) -> DataFrameGroupBy:
        return data.df.groupby(self.by_column_name)

    def save(self, data: D) -> None:
        objs = []
        for (by), df in self.group_by(data=data):
            objs.append({
                "bucket_name": self.bucket_name,
                "key": self.s3_key_by(tag=data.tag, by=by),
                "data": Data.df_to_json(df).encode('utf-8')
            })

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.provider.s3_save_objects_bulk(objs=objs))


class TagTagsAnalyticsDaoAwsS3(TagsAnalyticsDaoAwsS3[T, D], ABC):

    @staticmethod
    @abstractmethod
    def s3_key(tag: T) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def s3_key_by(tag: T, by: str) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def by_column_name(self) -> str:
        raise NotImplementedError

    def data_df(self, data: D) -> pd.DataFrame:
        return data.df

    def group_by(self, data: D) -> pd.core.groupby.DataFrameGroupBy:
        return data.df.groupby(self.by_column_name)

    def save(self, data: D) -> None:
        objs = [{
            "bucket_name": self.bucket_name,
            "key": self.s3_key(tag=data.tag),
            "data": Data.df_to_json(self.data_df(data)).encode('utf-8')
        }]

        for (by), df in self.group_by(data=data):
            objs.append({
                "bucket_name": self.bucket_name,
                "key": self.s3_key_by(tag=data.tag, by=by),
                "data": Data.df_to_json(df).encode('utf-8')
            })

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.provider.s3_save_objects_bulk(objs=objs))
