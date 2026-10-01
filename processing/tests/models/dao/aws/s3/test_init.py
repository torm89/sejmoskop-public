from unittest.mock import PropertyMock, Mock


def test_fetch_s3_object(mock_dao_aws_s3):
    type(mock_dao_aws_s3).bucket_name = PropertyMock(return_value='fake_bucket_name')
    mock_dao_aws_s3.s3_key = Mock(return_value='fake_s3_key')
    mock_dao_aws_s3.provider.s3_get_object = Mock(return_value='fake_s3_object')

    obj = mock_dao_aws_s3.fetch_s3_object('fake_tag')

    mock_dao_aws_s3.s3_key.assert_called_once_with(tag='fake_tag')
    mock_dao_aws_s3.provider.s3_get_object.assert_called_once_with(bucket_name='fake_bucket_name', key='fake_s3_key')
    assert obj == 'fake_s3_object'


def test_save(mock_dao_aws_s3):
    fake_data = Mock()
    fake_data.tag = 'fake_tag'
    fake_data.to_file_bytes = Mock(return_value='fake_data')

    type(mock_dao_aws_s3).bucket_name = PropertyMock(return_value='fake_bucket_name')
    mock_dao_aws_s3.s3_key = Mock(return_value='fake_s3_key')
    mock_dao_aws_s3.provider.s3_save_object = Mock()

    mock_dao_aws_s3.save(fake_data)

    # TODO: Fix this
    # mock_dao_aws_s3.s3_key.assert_called_once_with(tag='fake_tag')
    # mock_dao_aws_s3.provider.s3_save_object.assert_called_once_with(
    #     bucket_name='fake_bucket_name', key='fake_s3_key', data='fake_data')
