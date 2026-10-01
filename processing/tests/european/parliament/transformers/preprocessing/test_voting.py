import json
from datetime import datetime

from processing.models.tags import VotingOutcomeTag, VotingType
from processing.transformers.processing.european.parliament.voting import VotingProcessingTransformerEuropeanParliament


def test_add_datetime_field(voting_data_9_1_166077):
    data, tag = voting_data_9_1_166077

    assert VotingProcessingTransformerEuropeanParliament.add_datetime_field(tag, data) == {
        **data,
        "datetime": datetime(2024, 3, 12, 0, 0, 0).isoformat()
    }


def test_add_description_01_field(voting_data_9_1_166077):
    data, tag = voting_data_9_1_166077

    assert VotingProcessingTransformerEuropeanParliament.add_description_01_field(tag, data) == {
        **data,
        "description_01": ""
    }


def test_add_description_02_field(voting_data_9_1_166077):
    data, tag = voting_data_9_1_166077

    assert VotingProcessingTransformerEuropeanParliament.add_description_02_field(tag, data) == {
        **data,
        "description_02": "- Sophia in 't Veld - Wstępne porozumienie - Popr. 92"
    }


def test_add_description_03_field(voting_data_9_1_166077):
    data, tag = voting_data_9_1_166077

    assert VotingProcessingTransformerEuropeanParliament.add_description_03_field(tag, data) == {
        **data,
        "description_03": ""
    }


def test_fix_voting_type_field_normal(voting_data_9_1_166077):
    data, tag = voting_data_9_1_166077

    assert VotingProcessingTransformerEuropeanParliament.fix_voting_type_field(tag, data) == {
        **data,
        "votingType": VotingType.NORMAL
    }


def test_extract_voting_outcomes(reference_european_parliament_transformers_processing_path, voting_data_9_1_166077):
    data, tag = voting_data_9_1_166077

    outcome_data, outcome_tag = \
        VotingProcessingTransformerEuropeanParliament.extract_voting_outcomes(tag, data)

    reference_data_path = reference_european_parliament_transformers_processing_path / f"votings_outcomes_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    # reference_data_path.open('w+').write(json.dumps(outcome_data, indent=4))

    assert outcome_tag == VotingOutcomeTag(**outcome_tag.model_dump(by_alias=True))
    assert outcome_data[:50] == json.load(reference_data_path.open(encoding='utf-8'))[:50]


def test_extract_voting_outcomes_intentions(reference_european_parliament_transformers_processing_path,
                                            voting_data_9_1_166284):
    data, tag = voting_data_9_1_166284

    outcome_data, outcome_tag = \
        VotingProcessingTransformerEuropeanParliament.extract_voting_outcomes(tag, data)

    reference_data_path = reference_european_parliament_transformers_processing_path / f"votings_outcomes_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    # reference_data_path.open('w+').write(json.dumps(outcome_data, indent=4))

    assert outcome_tag == VotingOutcomeTag(**outcome_tag.model_dump(by_alias=True))
    assert outcome_data[:50] == json.load(reference_data_path.open(encoding='utf-8'))[:50]


def test_extract_voting_outcomes_strange_format(reference_european_parliament_transformers_processing_path,
                                                voting_data_9_73_125262):
    data, tag = voting_data_9_73_125262

    outcome_data, outcome_tag = \
        VotingProcessingTransformerEuropeanParliament.extract_voting_outcomes(tag, data)

    reference_data_path = reference_european_parliament_transformers_processing_path / f"votings_outcomes_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    # reference_data_path.open('w+').write(json.dumps(outcome_data, indent=4))

    assert outcome_tag == VotingOutcomeTag(**outcome_tag.model_dump(by_alias=True))
    assert outcome_data[:50] == json.load(reference_data_path.open(encoding='utf-8'))[:50]


def test_extract_voting_outcomes_empty_against(reference_european_parliament_transformers_processing_path,
                                               voting_data_9_154_141899):
    data, tag = voting_data_9_154_141899

    outcome_data, outcome_tag = \
        VotingProcessingTransformerEuropeanParliament.extract_voting_outcomes(tag, data)

    reference_data_path = reference_european_parliament_transformers_processing_path / f"votings_outcomes_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    # reference_data_path.open('w+').write(json.dumps(outcome_data, indent=4))

    assert outcome_tag == VotingOutcomeTag(**outcome_tag.model_dump(by_alias=True))
    assert outcome_data[:50] == json.load(reference_data_path.open(encoding='utf-8'))[:50]
