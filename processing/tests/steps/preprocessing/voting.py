from unittest.mock import patch, Mock, call

from processing.models.tags import VotingTag
from processing.steps.processing.sejm.voting import VotingProcessingStepSejm


@patch('processing.transformers.sejm.processing.voting_hot_data.VotingPreprocessingTransformer.add_datetime_field')
@patch('processing.transformers.sejm.processing.voting_hot_data.VotingPreprocessingTransformer.fix_voting_type_field')
@patch('processing.transformers.sejm.processing.voting_hot_data.VotingPreprocessingTransformer.extract_outcome')
def test_run(extract_outcome_mock, fix_voting_type_field_mock, add_datetime_field_mock):
    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    voting_data = []

    add_datetime_field_mock.return_value = voting_data
    fix_voting_type_field_mock.return_value = voting_data
    extract_outcome_mock.return_value = [voting_tag, voting_data]

    mock_manager = Mock()
    mock_manager.attach_mock(add_datetime_field_mock, 'add_datetime_field_mock')
    mock_manager.attach_mock(fix_voting_type_field_mock, 'fix_voting_type_field_mock')
    mock_manager.attach_mock(extract_outcome_mock, 'extract_outcome_mock')

    payload = {"voting_tag": voting_tag, "voting_data": voting_data}
    payload = VotingProcessingStepSejm().run(payload)

    # assert calling order
    assert mock_manager.mock_calls == [
        call.add_datetime_field_mock(tag=voting_tag, data=voting_data),
        call.fix_voting_type_field_mock(tag=voting_tag, data=voting_data),
        call.extract_outcome_mock(tag=voting_tag, data=voting_data),
    ]
