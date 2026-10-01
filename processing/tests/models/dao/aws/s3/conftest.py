from unittest.mock import MagicMock

import pytest

from processing.models.dao import T, D
from processing.models.dao.aws.s3 import DaoAwsS3
from processing.models.dao.aws.s3.preprocessing.group import GroupHotDaoAwsS3, GroupDaoAwsS3, GroupImageDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.member import MemberDaoAwsS3, MemberHotDaoAwsS3, MemberImageDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.voting import VotingDaoAwsS3, VotingHotDaoAwsS3, VotingOutcomeDaoAwsS3
from processing.models.tags import TermTag


class MockDaoAwsS3(DaoAwsS3):

    def save(self, data: D) -> None:
        pass

    @staticmethod
    def s3_prefix(term_tag: TermTag) -> str:
        pass

    @staticmethod
    def tag_from_s3_key(key=str) -> T:
        pass

    @property
    def bucket_name(self) -> str:
        pass

    @staticmethod
    def s3_key(tag: T) -> str:
        pass

    def get(self, tag: T) -> D:
        pass


@pytest.fixture
def mock_dao_aws_s3():
    dao = MockDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def member_hot_dao_aws_s3():
    dao = MemberHotDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def member_dao_aws_s3():
    dao = MemberDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def member_image_dao_aws_s3():
    dao = MemberImageDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def group_hot_dao_aws_s3():
    dao = GroupHotDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def group_dao_aws_s3():
    dao = GroupDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def group_image_dao_aws_s3():
    dao = GroupImageDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def voting_hot_dao_aws_s3():
    dao = VotingHotDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def voting_dao_aws_s3():
    dao = VotingDaoAwsS3()
    dao.provider = MagicMock()
    return dao


@pytest.fixture
def voting_outcome_dao_aws_s3():
    dao = VotingOutcomeDaoAwsS3()
    dao.provider = MagicMock()
    return dao

