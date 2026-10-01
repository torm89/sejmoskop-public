import json
import os
from abc import abstractmethod, ABC
from typing import List, Generic, TypeVar

from processing.models.tags import VotingTag, MemberTag, FakeTag, GroupTag, StatementTag, LegislationTag
from processing.providers.aws import AwsProvider
from processing.utils.utils import chunks

T = TypeVar('T', MemberTag, VotingTag, GroupTag, StatementTag, FakeTag, LegislationTag)


class BatchManager(Generic[T], ABC):

    def __init__(self):
        self.provider = AwsProvider()

    @property
    def payload_bucket_name(self):
        return os.getenv('AWS_S3_BATCH_DISPATCHER_BUCKET_NAME')

    @property
    def aws_batch_job_array_index(self):
        return int(os.getenv('AWS_BATCH_JOB_ARRAY_INDEX'))

    @abstractmethod
    def tags_per_job(self, tag=None) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def payload_s3_key_prefix(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def type_adapter_list(self):
        raise NotImplementedError

    def payload_s3_key(self, payload_id: str) -> str:
        return f"{self.payload_s3_key_prefix}/{payload_id}.json"

    def payload_tags_to_process_s3_key(self, payload_id: str) -> str:
        return f"{self.payload_s3_key_prefix}/tags_to_process/{payload_id}.json"

    def payload_tags_previously_processed_s3_key(self, payload_id: str) -> str:
        return f"{self.payload_s3_key_prefix}/tags_previously_processed/{payload_id}.json"

    @staticmethod
    def dump_tags(tags: List[T]):
        return [t.model_dump(by_alias=True) for t in tags]

    def dump_and_chunk_tags(self, tags: List[T]):
        tags_dumped = self.dump_tags(tags)
        tags_dumped_chunked = list(chunks(tags_dumped, self.tags_per_job(tags[0] if tags else None)))

        # AWS Batch doesn't allow "index array" size == 1
        if len(tags_dumped_chunked) == 1:
            tags_dumped_chunked.append([])

        return tags_dumped_chunked

    def save_payload(self, tags_dumped_chunked: List[str], payload_id: str):
        data = json.dumps(tags_dumped_chunked, indent=2).encode('utf-8')

        self.provider.s3_save_object(
            bucket_name=self.payload_bucket_name, key=self.payload_s3_key(payload_id), data=data)

    def save_payload_tags_to_process(self, tags: List[T], payload_id: str):
        tags_dumped = self.dump_tags(tags)
        data = json.dumps(tags_dumped, indent=2).encode('utf-8')

        self.provider.s3_save_object(
            bucket_name=self.payload_bucket_name, key=self.payload_tags_to_process_s3_key(payload_id), data=data)

    def save_payload_tags_previously_processed(self, tags: List[T], payload_id: str):
        tags_dumped = self.dump_tags(tags)
        data = json.dumps(tags_dumped, indent=2).encode('utf-8')

        self.provider.s3_save_object(
            bucket_name=self.payload_bucket_name, key=self.payload_tags_previously_processed_s3_key(payload_id),
            data=data
        )

    def get_payload(self, payload_id) -> List[T]:
        data = self.provider.s3_get_object(bucket_name=self.payload_bucket_name, key=self.payload_s3_key(payload_id))
        return json.loads(data)

    def get_payload_tags_to_process(self, payload_id) -> List[T]:
        data = self.provider.s3_get_object(
            bucket_name=self.payload_bucket_name, key=self.payload_tags_to_process_s3_key(payload_id))

        return self.type_adapter_list.validate_python(json.loads(data))

    def get_payload_previously_processed(self, payload_id) -> List[T]:
        data = self.provider.s3_get_object(
            bucket_name=self.payload_bucket_name, key=self.payload_tags_previously_processed_s3_key(payload_id))

        return self.type_adapter_list.validate_python(json.loads(data))

    def find_payload(self, payload_id) -> List[T]:
        tags_to_process = self.get_payload_tags_to_process(payload_id)
        tags_previously_processed = self.get_payload_previously_processed(payload_id)

        return list(set(tags_to_process) - set(tags_previously_processed))

    def get_tags_from_payload(self, payload_id):
        payload = self.get_payload(payload_id)
        idx = self.aws_batch_job_array_index

        return self.type_adapter_list.validate_python(payload[idx])
