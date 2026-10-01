import os
from unittest.mock import PropertyMock, Mock, patch

from processing.models.tags import FakeTag


@patch.dict(os.environ, {"AWS_S3_BATCH_DISPATCHER_BUCKET_NAME": "fake_bucket_name"}, clear=True)
def test_payload_bucket_name(batch_manager_mock):
    assert batch_manager_mock.payload_bucket_name == "fake_bucket_name"


@patch.dict(os.environ, {"AWS_BATCH_JOB_ARRAY_INDEX": "2"}, clear=True)
def test_aws_batch_job_array_index(batch_manager_mock):
    assert batch_manager_mock.aws_batch_job_array_index == 2


def test_get_payload(batch_manager_mock):
    type(batch_manager_mock).payload_bucket_name = PropertyMock(return_value='fake_bucket_name')
    batch_manager_mock.payload_s3_key = Mock(return_value='fake_s3_key')
    batch_manager_mock.provider.s3_get_object = Mock(return_value='{"tags":["tag1", "tag2"],"tagsPerBatchJob":2}')

    payload = batch_manager_mock.get_payload('fake_payload_id')

    batch_manager_mock.payload_s3_key.assert_called_once_with('fake_payload_id')
    batch_manager_mock.provider.s3_get_object.assert_called_once_with(bucket_name='fake_bucket_name', key='fake_s3_key')
    assert payload == {"tags": ["tag1", "tag2"], "tagsPerBatchJob": 2}


def test_get_tags_from_payload(batch_manager_mock):
    type(batch_manager_mock).aws_batch_job_array_index = PropertyMock(return_value=2)
    batch_manager_mock.payload_s3_key = Mock(return_value='fake_s3_key')
    batch_manager_mock.get_payload = Mock(
        return_value=[[{"a": "b1"}, {"a": "b2"}], [{"a": "b3"}, {"a": "b4"}], [{"a": "b5"}]])

    tags = batch_manager_mock.get_tags_from_payload('fake_payload_id')

    batch_manager_mock.get_payload.assert_called_once_with('fake_payload_id')
    assert tags == [{"a": "b5"}]
