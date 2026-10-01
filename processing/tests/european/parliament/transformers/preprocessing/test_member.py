import json

import pytest

from processing.models.tags import MemberType
from processing.transformers.processing.european.parliament.member import MemberProcessingTransformerEuropeanParliament


def test_add_member_name_fields(members_9_124807):
    data, tag = members_9_124807
    data = MemberProcessingTransformerEuropeanParliament.add_member_name_fields(tag, data)

    assert data['firstName'] == 'Jens'
    assert data['lastName'] == 'Gieseke'
    assert data['secondName'] == ''


def test_add_member_name_fields_second_name(members_9_197612):
    data, tag = members_9_197612
    data = MemberProcessingTransformerEuropeanParliament.add_member_name_fields(tag, data)

    assert data['firstName'] == 'Annunziata'
    assert data['lastName'] == 'Rees-Mogg'
    assert data['secondName'] == 'Mary'


@pytest.mark.skip(reason="TODO: Fix encoding issue in the test data.")
def test_add_member_name_fields_encoding(members_9_96752):
    data, tag = members_9_96752
    data = MemberProcessingTransformerEuropeanParliament.add_member_name_fields(tag, data)

    assert data['firstName'] == 'Martin'
    assert data['lastName'] == ''
    assert data['secondName'] == 'Häusling'


def test_add_member_voting_name_field(members_9_124807):
    data, tag = members_9_124807
    data = MemberProcessingTransformerEuropeanParliament.add_member_voting_name_field(tag, data)

    assert data['votingName'] == '124807'


def test_fix_member_type_field(members_9_124807):
    data, tag = members_9_124807
    data = MemberProcessingTransformerEuropeanParliament.fix_member_type_field(tag, data)

    assert data['memberType'] == MemberType.ACTIVE


def test_fix_member_type_field_active_new(members_9_239973):
    data, tag = members_9_239973
    data = MemberProcessingTransformerEuropeanParliament.fix_member_type_field(tag, data)

    assert data['memberType'] == MemberType.ACTIVE


def test_fix_member_type_field_former(members_9_197612):
    data, tag = members_9_197612
    data = MemberProcessingTransformerEuropeanParliament.fix_member_type_field(tag, data)

    assert data['memberType'] == MemberType.FORMER


def test_add_former_details_field(members_9_124807):
    data, tag = members_9_124807
    data = MemberProcessingTransformerEuropeanParliament.add_former_details_field(tag, data)

    assert data['former_details'] == json.dumps({})


def test_add_former_details_field_active_new(members_9_239973):
    data, tag = members_9_239973
    data = MemberProcessingTransformerEuropeanParliament.add_former_details_field(tag, data)

    assert data['former_details'] == json.dumps({
        "mandate_start": "2022-11-22",
    })


def test_add_former_details_field_former(members_9_197612):
    data, tag = members_9_197612
    data = MemberProcessingTransformerEuropeanParliament.add_former_details_field(tag, data)

    assert data['former_details'] == json.dumps({
        "mandate_start": "2019-07-02",
        "mandate_end": "2020-01-31",
    })


def test_add_member_birth_date_field(members_9_197612):
    data, tag = members_9_197612
    data = MemberProcessingTransformerEuropeanParliament.add_member_birth_date_field(tag, data)

    assert data['birthDate'] == '-'
