from unittest.mock import Mock, MagicMock

from processing.models.data.preprocessing.member import MemberData, MemberImageData
from processing.models.data.preprocessing.voting import VotingData, VotingOutcomeData


def test_fetch_member_hot_data(mock_s3_repository):
    fake_member_tag = "fake_member_tag"
    mock_s3_repository.member_hot_dao_aws_s3.get = Mock(return_value='fake_member_hot_data')

    assert mock_s3_repository.fetch_member_hot_data(fake_member_tag) == 'fake_member_hot_data'
    mock_s3_repository.member_hot_dao_aws_s3.get.assert_called_once_with(tag=fake_member_tag)


def test_fetch_voting_hot_data(mock_s3_repository):
    fake_voting_tag = "fake_voting_tag"
    mock_s3_repository.voting_hot_dao_aws_s3.get = Mock(return_value='fake_voting_hot_data')

    assert mock_s3_repository.fetch_voting_hot_data(fake_voting_tag) == 'fake_voting_hot_data'
    mock_s3_repository.voting_hot_dao_aws_s3.get.assert_called_once_with(tag=fake_voting_tag)


def test_save_member_data(mock_s3_repository):
    fake_member_data = MagicMock(MemberData)
    mock_s3_repository.member_dao_aws_s3.save = Mock()

    assert mock_s3_repository.save(fake_member_data) is None
    mock_s3_repository.member_dao_aws_s3.save.assert_called_once_with(data=fake_member_data)


def test_save_member_image_data(mock_s3_repository):
    fake_member_image_data = MagicMock(MemberImageData)
    mock_s3_repository.member_image_dao_aws_s3.save = Mock()

    assert mock_s3_repository.save(fake_member_image_data) is None
    mock_s3_repository.member_image_dao_aws_s3.save.assert_called_once_with(data=fake_member_image_data)


def test_save_voting_data(mock_s3_repository):
    fake_voting_data = MagicMock(VotingData)
    mock_s3_repository.voting_dao_aws_s3.save = Mock()

    assert mock_s3_repository.save(fake_voting_data) is None
    mock_s3_repository.voting_dao_aws_s3.save.assert_called_once_with(data=fake_voting_data)


def test_save_voting_outcome_data(mock_s3_repository):
    fake_voting_outcome_data = MagicMock(VotingOutcomeData)
    mock_s3_repository.voting_outcome_dao_aws_s3.save = Mock()

    assert mock_s3_repository.save(fake_voting_outcome_data) is None
    mock_s3_repository.voting_outcome_dao_aws_s3.save.assert_called_once_with(data=fake_voting_outcome_data)
