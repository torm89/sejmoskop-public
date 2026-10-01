import os
from unittest.mock import Mock, patch

import pytest

from processing.models.tags import VotingTag, VotingOutcomeTag, VotingType


@patch.dict(os.environ, {"AWS_S3_HOT_DATA_BUCKET_NAME": "fake_aws_s3_hot_data_bucket_name"}, clear=True)
def test_voting_hot_dao_aws_s3_bucket_name(voting_hot_dao_aws_s3):
    assert voting_hot_dao_aws_s3.bucket_name == "fake_aws_s3_hot_data_bucket_name"


def test_voting_hot_dao_aws_s3_s3_key(voting_hot_dao_aws_s3):
    fake_voting_tag = VotingTag(chamberName="sejm", termId="10", sessionId="2", votingId="3")

    assert voting_hot_dao_aws_s3.s3_key(fake_voting_tag) == 'sejm/10/votings/2/3.json'


def test_voting_hot_dao_aws_s3_get(voting_hot_dao_aws_s3):
    fake_voting_tag = VotingTag(chamberName="sejm", termId="10", sessionId="2", votingId="3")
    voting_hot_dao_aws_s3.fetch_s3_object = Mock(return_value="{\"fake key\": \"fake value\"}")

    assert voting_hot_dao_aws_s3.get(fake_voting_tag) == {"fake key": "fake value"}
    voting_hot_dao_aws_s3.fetch_s3_object.assert_called_once_with(tag=fake_voting_tag)


def test_voting_hot_dao_aws_s3_save(voting_hot_dao_aws_s3):
    with pytest.raises(NotImplementedError):
        voting_hot_dao_aws_s3.save({})


@patch.dict(os.environ, {"AWS_S3_DATA_BUCKET_NAME": "fake_aws_s3_data_bucket_name"}, clear=True)
def test_voting_dao_aws_s3_bucket_name(voting_dao_aws_s3):
    assert voting_dao_aws_s3.bucket_name == "fake_aws_s3_data_bucket_name"


def test_voting_dao_aws_s3_s3_key(voting_dao_aws_s3):
    fake_voting_tag = VotingTag(chamberName="sejm", termId="10", sessionId="2", votingId="3")

    assert voting_dao_aws_s3.s3_key(fake_voting_tag) == f'tables/votings/chamber_name=sejm/term_id=10/2/3.csv'


@pytest.mark.skip(reason="Actually implemented now")
def test_voting_dao_aws_s3_get(voting_dao_aws_s3):
    fake_voting_tag = VotingTag(chamberName="sejm", termId="10", sessionId="2", votingId="3")

    with pytest.raises(NotImplementedError):
        assert voting_dao_aws_s3.get(fake_voting_tag)


@patch.dict(os.environ, {"AWS_S3_DATA_BUCKET_NAME": "fake_aws_s3_data_bucket_name"}, clear=True)
def test_voting_outcome_dao_aws_s3_bucket_name(voting_outcome_dao_aws_s3):
    assert voting_outcome_dao_aws_s3.bucket_name == "fake_aws_s3_data_bucket_name"


def test_voting_outcome_dao_aws_s3_s3_key(voting_outcome_dao_aws_s3):
    fake_voting_outcome_tag = VotingOutcomeTag(chamberName="sejm", termId="10", sessionId="2", votingId="3")

    assert voting_outcome_dao_aws_s3.s3_key(
        fake_voting_outcome_tag) == 'tables/votings_outcomes/chamber_name=sejm/term_id=10/2/3.csv'


@pytest.mark.skip(reason="Actually implemented now")
def test_voting_outcome_dao_aws_s3_get(voting_outcome_dao_aws_s3):
    fake_voting_outcome_tag = VotingOutcomeTag(chamberName="sejm", termId="10", sessionId="2", votingId="3")

    with pytest.raises(NotImplementedError):
        assert voting_outcome_dao_aws_s3.get(fake_voting_outcome_tag)
