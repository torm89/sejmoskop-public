import os
from unittest.mock import Mock, patch

import pytest

from processing.models.tags import MemberTag


@patch.dict(os.environ, {"AWS_S3_HOT_DATA_BUCKET_NAME": "fake_aws_s3_hot_data_bucket_name"}, clear=True)
def test_member_hot_dao_aws_s3_bucket_name(member_hot_dao_aws_s3):
    assert member_hot_dao_aws_s3.bucket_name == "fake_aws_s3_hot_data_bucket_name"


def test_member_hot_dao_aws_s3_s3_key(member_hot_dao_aws_s3):
    fake_member_tag = MemberTag(chamberName="sejm", termId="10", memberId="010")

    assert member_hot_dao_aws_s3.s3_key(fake_member_tag) == 'sejm/10/members/010.json'


def test_member_hot_dao_aws_s3_get(member_hot_dao_aws_s3):
    fake_member_tag = MemberTag(chamberName="sejm", termId="10", memberId="010")
    member_hot_dao_aws_s3.fetch_s3_object = Mock(return_value="{\"fake key\": \"fake value\"}")

    assert member_hot_dao_aws_s3.get(fake_member_tag) == {"fake key": "fake value"}
    member_hot_dao_aws_s3.fetch_s3_object.assert_called_once_with(tag=fake_member_tag)


def test_member_hot_dao_aws_s3_save(member_hot_dao_aws_s3):
    with pytest.raises(NotImplementedError):
        member_hot_dao_aws_s3.save({})


@patch.dict(os.environ, {"AWS_S3_DATA_BUCKET_NAME": "fake_aws_s3_data_bucket_name"}, clear=True)
def test_member_dao_aws_s3_bucket_name(member_dao_aws_s3):
    assert member_dao_aws_s3.bucket_name == "fake_aws_s3_data_bucket_name"


def test_member_dao_aws_s3_s3_key(member_dao_aws_s3):
    fake_member_tag = MemberTag(chamberName="sejm", termId="10", memberId="011")

    assert member_dao_aws_s3.s3_key(fake_member_tag) == f'tables/members/chamber_name=sejm/term_id=10/011.json'


def test_member_dao_aws_s3_get(member_dao_aws_s3):
    fake_member_tag = MemberTag(chamberName="sejm", termId="10", memberId="010")

    with pytest.raises(NotImplementedError):
        assert member_dao_aws_s3.get(fake_member_tag)


@patch.dict(os.environ, {"AWS_S3_DATA_BUCKET_NAME": "fake_aws_s3_data_bucket_name"}, clear=True)
def test_member_image_dao_aws_s3_bucket_name(member_image_dao_aws_s3):
    assert member_image_dao_aws_s3.bucket_name == "fake_aws_s3_data_bucket_name"


def test_member_image_dao_aws_s3_s3_key(member_image_dao_aws_s3):
    fake_member_tag = MemberTag(chamberName="sejm", termId="10", memberId="011")

    assert member_image_dao_aws_s3.s3_key(fake_member_tag) == 'images/members/sejm/10/011.jpg'


# def test_member_image_dao_aws_s3_get(member_image_dao_aws_s3):
#     with pytest.raises(NotImplementedError):
#         member_image_dao_aws_s3.get({})
