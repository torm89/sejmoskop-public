from processing.transformers.processing.european.parliament.group import GroupProcessingTransformerEuropeanParliament


def test_add_group_name_short_field(group_data_grupa_renew_europe):
    data, tag = group_data_grupa_renew_europe

    data = GroupProcessingTransformerEuropeanParliament.add_group_name_short_field(tag=tag, data=data)

    assert data['nameShort'] == 'Grupa Renew Europe'


def test_add_group_type_field(group_data_grupa_renew_europe):
    data, tag = group_data_grupa_renew_europe

    data = GroupProcessingTransformerEuropeanParliament.add_group_type_field(tag=tag, data=data)

    assert data['groupType'] == ''
