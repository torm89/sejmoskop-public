import json

from processing.steps.processing.european.parliament.group import GroupProcessingStepEuropeanParliament


def test_group_processing_step_european_parliament(
        group_data_grupa_renew_europe, reference_european_parliament_steps_processing_path):
    data, tag = group_data_grupa_renew_europe

    payload = {
        'group_tag': tag,
        'group_data': data
    }

    step = GroupProcessingStepEuropeanParliament()
    payload = step.run(payload)
    group_data_dict = payload['group_data'].df_dict()

    reference_data_path = reference_european_parliament_steps_processing_path / "group_processing_step_european_parliament_group_data_grupa_renew_europe.json"
    # reference_data_path.open('w+').write(json.dumps(group_data_dict, indent=4))

    assert group_data_dict == json.load(reference_data_path.open(encoding='utf-8'))
