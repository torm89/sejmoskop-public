import json

from processing.steps.processing.european.parliament.statement import StatementProcessingStepEuropeanParliament


def test_statement_processing_step_european_parliament_9_2024_03_12_10_5(
        statements_9_2024_03_12_10_5, reference_european_parliament_steps_processing_path):
    data, tag = statements_9_2024_03_12_10_5

    payload = {
        'statement_tag': tag,
        'statement_data': data,
    }

    step = StatementProcessingStepEuropeanParliament()
    payload = step.run(payload)

    statement_data = payload['statement_data']

    reference_data_dict_path = reference_european_parliament_steps_processing_path / "statement_processing_step_european_parliament_9_2024_03_12_10_5.json"
    # reference_data_dict_path.open('w+').write(json.dumps({
    #     'statement_data': statement_data,
    # }, indent=4))

    assert statement_data == json.load(reference_data_dict_path.open(encoding='utf-8'))['statement_data']


def test_statement_processing_step_european_parliament_9_2024_03_12_12_9(
        statements_9_2024_03_12_12_9, reference_european_parliament_steps_processing_path):
    data, tag = statements_9_2024_03_12_12_9

    payload = {
        'statement_tag': tag,
        'statement_data': data,
    }

    step = StatementProcessingStepEuropeanParliament()
    payload = step.run(payload)

    statement_data = payload['statement_data']

    reference_data_dict_path = reference_european_parliament_steps_processing_path / "statement_processing_step_european_parliament_9_2024_03_12_12_9.json"
    # reference_data_dict_path.open('w+').write(json.dumps({
    #     'statement_data': statement_data,
    # }, indent=4))

    assert statement_data == json.load(reference_data_dict_path.open(encoding='utf-8'))['statement_data']


def test_statement_processing_step_european_parliament_9_2020_06_18_3_39(
        statements_9_2020_06_18_3_39, reference_european_parliament_steps_processing_path):
    data, tag = statements_9_2020_06_18_3_39

    payload = {
        'statement_tag': tag,
        'statement_data': data,
    }

    step = StatementProcessingStepEuropeanParliament()
    payload = step.run(payload)

    statement_data = payload['statement_data']

    reference_data_dict_path = reference_european_parliament_steps_processing_path / "statement_processing_step_european_parliament_9_2020_06_18_3_39.json"
    # reference_data_dict_path.open('w+').write(json.dumps({
    #     'statement_data': statement_data,
    # }, indent=4))

    assert statement_data == json.load(reference_data_dict_path.open(encoding='utf-8'))['statement_data']
