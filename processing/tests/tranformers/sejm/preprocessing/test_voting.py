from datetime import datetime
from unittest.mock import patch

import pytest

from processing.models.tags import VotingTag, VotingOutcomeTag, VotingType, VotingOutcomeCall
from processing.transformers.processing.sejm.voting import VotingProcessingTransformerSejm
from processing.utils.exceptions import NotHandleVotingTypeException


@pytest.mark.skip
def test_add_datetime_field():
    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    data = {"fake_field": "fake_value", "date": "12-11-2020", "time": "16:38:20"}

    assert VotingProcessingTransformerSejm.add_datetime_field(voting_tag, data) == {
        **data,
        "datetime": datetime(2020, 11, 12, 16, 38, 20)
    }


def test_fix_voting_type_field_key_error():
    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    data = {"chamberName": "sejm", "termId": "10", "sessionId": "1", "votingId": "10", "votingType": "asdasda"}

    with pytest.raises(KeyError):
        VotingProcessingTransformerSejm.fix_voting_type_field(voting_tag, data)


@pytest.mark.parametrize(
    "data_extends, expected_voting_type",
    [
        ({"votingType": "ELECTRONIC"}, VotingType.NORMAL),
        ({"votingType": "ON_LIST"}, VotingType.LIST),
        ({"votingType": "TRADITIONAL"}, VotingType.TRADITIONAL),
        ({"votingType": "ELECTRONIC", "description02": "Głosowanie kworum"}, VotingType.QUORUM)
    ])
def test_fix_voting_type_field_normal(data_extends, expected_voting_type):
    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    data = {"chamberName": "sejm", "termId": "10", "sessionId": "1", "votingId": "10", **data_extends}

    assert VotingProcessingTransformerSejm.fix_voting_type_field(voting_tag, data) == {
        **data,
        "votingType": expected_voting_type
    }


@pytest.mark.skip
def test__extract_outcome_normal_voting():
    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    data = {
        "chamberName": "sejm",
        "termId": "10",
        "sessionId": "1",
        "votingId": "10",
        "votingType": "normal",
        "outcome": [
            {"memberName": "Adamczyk Andrzej", "groupName": "PiS", "call": "Za"},
            {"memberName": "Andruszkiewicz Adam", "groupName": "PiS", "call": "Za"}
        ]
    }

    outcome_data, outcome_tag = VotingProcessingTransformerSejm._extract_outcome_normal_voting(voting_tag, data)

    assert outcome_tag == VotingOutcomeTag(
        chamberName="sejm", termId="9", sessionId="1", votingId="382", votingType="normal")
    assert outcome_data == [
        {"chamberName": "sejm", "termId": "10", "sessionId": "1", "votingId": "10", "votingType": "normal",
         "memberName": "Adamczyk Andrzej", "groupName": "PiS", "call": VotingOutcomeCall.yea},
        {"chamberName": "sejm", "termId": "10", "sessionId": "1", "votingId": "10", "votingType": "normal",
         "memberName": "Andruszkiewicz Adam", "groupName": "PiS", "call": VotingOutcomeCall.yea}
    ]


@patch(
    'processing.transformers.processing.sejm.voting.VotingProcessingTransformerSejm._extract_outcome_normal_voting')
def test_extract_outcome_normal(_extract_outcome_normal_voting_mock):
    _extract_outcome_normal_voting_mock.return_value = [1, 2]

    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    data = {
        "chamberName": "sejm", "termId": "10", "sessionId": "1", "votingId": "10", "votingType": "normal", "outcome": []
    }

    outcome_data, outcome_tag = VotingProcessingTransformerSejm.extract_outcome(voting_tag, data)
    _extract_outcome_normal_voting_mock.assert_called_once_with(voting_tag, data)

    assert outcome_data == 1
    assert outcome_tag == 2


@patch(
    'processing.transformers.processing.sejm.voting.VotingProcessingTransformerSejm._extract_outcome_normal_voting')
def test_extract_outcome(_extract_outcome_normal_voting_mock):
    _extract_outcome_normal_voting_mock.return_value = [1, 2]

    voting_tag = VotingTag(chamberName="sejm", termId="9", sessionId="1", votingId="382")
    data = {
        "chamberName": "sejm", "termId": "10", "sessionId": "1", "votingId": "10", "votingType": "asdas", "outcome": []
    }

    with pytest.raises(NotHandleVotingTypeException):
        VotingProcessingTransformerSejm.extract_outcome(voting_tag, data)
