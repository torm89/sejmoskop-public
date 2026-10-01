import json
from pathlib import Path

import pandas as pd
import pytest

from processing.models.data.preprocessing.member import MemberData
from processing.models.data.preprocessing.voting import VotingData, VotingOutcomeData
from processing.models.tags import TermTag, VotingTag, VotingOutcomeTag, MemberTag


@pytest.fixture(scope='session')
def reference_european_parliament_steps_enrichment_path(reference_european_parliament_path) -> Path:
    return reference_european_parliament_path / 'steps' / 'enrichment'


@pytest.fixture(scope='session')
def members_table_date_9_166277(data_european_parliament_path):
    tag = TermTag(chamberName="european-parliament", termId="9"),

    data_file_path = data_european_parliament_path / "members_table_data_9_166227.json"
    data = data_file_path.open(encoding='utf-8').read()

    return MemberData.from_json(tag=tag, data=data)


@pytest.fixture(scope='session')
def voting_processing_step_european_parliament_voting_data_9_1_166284(data_european_parliament_path):
    voting_tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="1", votingId="166284")
    voting_outcome_tag = VotingOutcomeTag(chamberName="european-parliament", termId="9", sessionId="1",
                                          votingId="166284")

    data_file_path = data_european_parliament_path / "voting_processing_step_european_parliament_voting_data_9_1_166284.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return {
        'voting_tag': voting_tag,
        'voting_data': VotingData.from_dict(tag=voting_tag, data=data['voting_data_dict']),
        'voting_outcome_data': VotingOutcomeData.from_dict(
            tag=voting_outcome_tag, data=data['voting_outcome_data_dict']),
    }


@pytest.fixture(scope='session')
def voting_processing_step_european_parliament_voting_data_9_73_125262(data_european_parliament_path):
    voting_tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="73", votingId="125262")
    voting_outcome_tag = VotingOutcomeTag(chamberName="european-parliament", termId="9", sessionId="73",
                                          votingId="125262")

    data_file_path = data_european_parliament_path / "voting_processing_step_european_parliament_voting_data_9_73_125262.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return {
        'voting_tag': voting_tag,
        'voting_data': VotingData.from_dict(tag=voting_tag, data=data['voting_data_dict']),
        'voting_outcome_data': VotingOutcomeData.from_dict(
            tag=voting_outcome_tag, data=data['voting_outcome_data_dict']),
    }


@pytest.fixture(scope='session')
def fake_member_voting_outcomes_9_166284(data_european_parliament_path):
    data_file_01_path = data_european_parliament_path / "member_voting_outcomes_9_239973_166227.json"
    data_file_02_path = data_european_parliament_path / "member_voting_outcomes_9_197842_166227.json"
    data_file_03_path = data_european_parliament_path / "member_voting_outcomes_9_197615_166227.json"

    return pd.concat([
        pd.read_json(data_file_01_path, orient='records'),
        pd.read_json(data_file_02_path, orient='records'),
        pd.read_json(data_file_03_path, orient='records'),
    ])


@pytest.fixture(scope='session')
def voting_outcome_no_voted_call_enrichment_step_european_parliament_9_1_166284(data_european_parliament_path):
    voting_tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="1", votingId="166284")
    voting_outcome_tag = VotingOutcomeTag(
        chamberName="european-parliament", termId="9", sessionId="1", votingId="166284")

    data_file_path = data_european_parliament_path / "voting_outcome_no_voted_call_enrichment_step_european_parliament_9_1_166284.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return {
        'voting_tag': voting_tag,
        'voting_data': VotingData.from_dict(tag=voting_tag, data=data['voting_data_dict']),
        'voting_outcome_data': VotingOutcomeData.from_dict(
            tag=voting_outcome_tag, data=data['voting_outcome_data_dict']),
    }


@pytest.fixture(scope='session')
def fake_members_with_dummy_group_name_short_9_member_names(data_european_parliament_path):
    with open(data_european_parliament_path / "members_with_dummy_group_name_short_9_member_names.json") as f:
        return json.load(f)


@pytest.fixture(scope='session')
def fake_member_tags_9(data_european_parliament_path):
    with open(data_european_parliament_path / "members_9.json") as f:
        return [MemberTag(**t) for t in json.load(f)]


@pytest.fixture(scope='session')
def fake_members_with_dummy_group_name_short_9_df(data_european_parliament_path):
    path = data_european_parliament_path / "members_with_dummy_group_name_short_9_df.json"
    return pd.read_json(path, orient='records', dtype=str)


@pytest.fixture(scope='session')
def fake_voting_outcome_data_9_1_166038(data_european_parliament_path):
    data = json.load((data_european_parliament_path / "voting_outcome_data_9_1_166038.json").open(encoding='utf-8'))
    return VotingOutcomeData.from_dict(tag=data['tag'], data=data['data'])


@pytest.fixture(scope='session')
def fake_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_166038(
        data_european_parliament_path):
    path = data_european_parliament_path / "member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_166038.json"
    return {VotingOutcomeTag.model_validate_json(k): v for el in json.load(path.open(encoding='utf-8')) for k, v in
            el.items()}
