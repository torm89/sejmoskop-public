from unittest.mock import Mock

import pytest

from processing.models.repositories.aws.s3 import S3Repository


@pytest.fixture
def mock_s3_repository():
    repository = S3Repository()
    repository.member_hot_dao_aws_s3 = Mock()
    repository.voting_hot_dao_aws_s3 = Mock()

    repository.member_dao_aws_s3 = Mock()
    repository.member_image_dao_aws_s3 = Mock()
    repository.voting_dao_aws_s3 = Mock()
    repository.voting_outcome_dao_aws_s3 = Mock()

    repository.member_dao_athena = Mock()
    repository.voting_dao_athena = Mock()

    return repository
