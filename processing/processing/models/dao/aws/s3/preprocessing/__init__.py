import os
from abc import ABC

from processing.models.dao import D, T
from processing.models.dao.aws.s3 import DaoAwsS3


class PreprocessingHotDaoAwsS3(DaoAwsS3[T, D], ABC):

    @property
    def bucket_name(self) -> str:
        return os.environ.get('AWS_S3_HOT_DATA_BUCKET_NAME')


class PreprocessingDaoAwsS3(PreprocessingHotDaoAwsS3[T, D], ABC):

    @property
    def bucket_name(self) -> str:
        return os.environ.get('AWS_S3_DATA_BUCKET_NAME')

    def save(self, data: D) -> None:
        self.provider.s3_save_object(
            bucket_name=self.bucket_name,
            key=self.s3_key(tag=data.tag),
            data=data.df_csv(header=False).encode('utf-8')
        )

    def get(self, tag: T) -> D:
        raise NotImplementedError
