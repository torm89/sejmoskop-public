import json

from processing.models.data.preprocessing.member import MemberImageData
from processing.steps.processing.european.parliament.member import MemberProcessingStepEuropeanParliament


def test_member_processing_step_european_parliament(
        members_9_197612, reference_european_parliament_steps_processing_path):
    data, tag = members_9_197612

    payload = {
        'member_tag': tag,
        'member_data': data,
        'member_current_image': MemberImageData.from_dict(tag=tag, data=b'fake_image')
    }

    step = MemberProcessingStepEuropeanParliament()
    payload = step.run(payload)

    member_data_dict = payload['member_data'].df_dict()

    reference_data_dict_path = reference_european_parliament_steps_processing_path / "member_processing_step_european_parliament_members_9_197612.json"
    # reference_data_dict_path.open('w+').write(json.dumps({
    #     'member_data': member_data_dict,
    # }, indent=4))

    assert member_data_dict == json.load(reference_data_dict_path.open(encoding='utf-8'))['member_data']
    # assert member_image_data == json.load(reference_data_dict_path.open(encoding='utf-8'))['member_image']
