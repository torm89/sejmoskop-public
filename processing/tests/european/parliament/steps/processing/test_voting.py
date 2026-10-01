import json

from processing.steps.processing.european.parliament.voting import VotingProcessingStepEuropeanParliament


def test_voting_processing_step_european_parliament_9_1_166284(
        voting_data_9_1_166284, reference_european_parliament_steps_processing_path):
    data, tag = voting_data_9_1_166284

    payload = {
        'voting_tag': tag,
        'voting_data': data,
    }

    step = VotingProcessingStepEuropeanParliament()
    payload = step.run(payload)

    voting_data_dict = payload['voting_data'].df_dict()
    voting_outcome_data_dict = payload['voting_outcome_data'].df_dict()

    reference_data_dict_path = reference_european_parliament_steps_processing_path / "voting_processing_step_european_parliament_voting_data_9_1_166284.json"
    # reference_data_dict_path.open('w+').write(json.dumps({
    #     'voting_data_dict': voting_data_dict,
    #     'voting_outcome_data_dict': voting_outcome_data_dict,
    # }, indent=4))

    assert voting_data_dict == json.load(reference_data_dict_path.open(encoding='utf-8'))['voting_data_dict']
    assert voting_outcome_data_dict == json.load(reference_data_dict_path.open(encoding='utf-8'))[
        'voting_outcome_data_dict']
