import json

import pytest

from processing.models.tags import MemberTag


@pytest.fixture(scope='session')
def fake_member_tag():
    return MemberTag(chamberName="sejm", termId="10", memberId="001")


@pytest.fixture(scope='session')
def fake_member_data(data_path, fake_member_tag):
    data_file_path = data_path / f"member_{fake_member_tag.chamber_name}_{fake_member_tag.term_id}_{fake_member_tag.member_id}.json"
    return json.load(data_file_path.open())


@pytest.fixture(scope='session')
def fake_member_image(data_path, fake_member_tag):
    image_file_path = data_path / f"member_{fake_member_tag.chamber_name}_{fake_member_tag.term_id}_{fake_member_tag.member_id}_image.jpg"
    return image_file_path.open("rb").read()
