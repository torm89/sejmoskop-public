from tests.models.data.init.conftest import MockDataHot


def test_form_json():
    fake_tag = "fake_tag"
    fake_data_json = "{\"fake key\": \"fake value\"}"
    fake_data = {"fake key": "fake value"}
    assert MockDataHot.from_json(tag=fake_tag, data=fake_data_json) == MockDataHot(tag=fake_tag, data=fake_data)
