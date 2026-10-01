import os
from unittest.mock import Mock, patch

import pytest

from processing.models.tags import GroupTag


@patch.dict(os.environ, {"AWS_S3_HOT_DATA_BUCKET_NAME": "fake_aws_s3_hot_data_bucket_name"}, clear=True)
def test_group_hot_dao_aws_s3_bucket_name(group_hot_dao_aws_s3):
    assert group_hot_dao_aws_s3.bucket_name == "fake_aws_s3_hot_data_bucket_name"


def test_group_hot_dao_aws_s3_s3_key(group_hot_dao_aws_s3):
    fake_group_tag = GroupTag(chamberName="sejm", termId="10", name="010")

    assert group_hot_dao_aws_s3.s3_key(fake_group_tag) == 'sejm/10/groups/010.json'


def test_group_hot_dao_aws_s3_get(group_hot_dao_aws_s3):
    fake_group_tag = GroupTag(chamberName="sejm", termId="10", name="010")
    group_hot_dao_aws_s3.fetch_s3_object = Mock(return_value="{\"fake key\": \"fake value\"}")

    assert group_hot_dao_aws_s3.get(fake_group_tag) == {"fake key": "fake value"}
    group_hot_dao_aws_s3.fetch_s3_object.assert_called_once_with(tag=fake_group_tag)


def test_group_hot_dao_aws_s3_save(group_hot_dao_aws_s3):
    with pytest.raises(NotImplementedError):
        group_hot_dao_aws_s3.save({})


@patch.dict(os.environ, {"AWS_S3_DATA_BUCKET_NAME": "fake_aws_s3_data_bucket_name"}, clear=True)
def test_group_dao_aws_s3_bucket_name(group_dao_aws_s3):
    assert group_dao_aws_s3.bucket_name == "fake_aws_s3_data_bucket_name"


def test_group_dao_aws_s3_s3_key(group_dao_aws_s3):
    fake_group_tag = GroupTag(chamberName="sejm", termId="10", name="011")

    assert group_dao_aws_s3.s3_key(fake_group_tag) == f'tables/groups/chamber_name=sejm/term_id=10/011.json'


def test_group_dao_aws_s3_get(group_dao_aws_s3):
    fake_group_tag = GroupTag(chamberName="sejm", termId="10", name="010")

    with pytest.raises(NotImplementedError):
        assert group_dao_aws_s3.get(fake_group_tag)


@patch.dict(os.environ, {"AWS_S3_DATA_BUCKET_NAME": "fake_aws_s3_data_bucket_name"}, clear=True)
def test_group_image_dao_aws_s3_bucket_name(group_image_dao_aws_s3):
    assert group_image_dao_aws_s3.bucket_name == "fake_aws_s3_data_bucket_name"


def test_group_image_dao_aws_s3_s3_key(group_image_dao_aws_s3):
    fake_group_tag = GroupTag(chamberName="sejm", termId="10", name="011")

    assert group_image_dao_aws_s3.s3_key(fake_group_tag) == 'images/groups/sejm/10/011.jpg'


def test_group_image_dao_aws_s3_get(group_image_dao_aws_s3):
    with pytest.raises(NotImplementedError):
        group_image_dao_aws_s3.get({})
