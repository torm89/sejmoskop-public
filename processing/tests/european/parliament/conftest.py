import json
from pathlib import Path

import pytest

from processing.models.tags import VotingTag, GroupTag, MemberTag, StatementTag


@pytest.fixture(scope='session')
def data_european_parliament_path(base_path) -> Path:
    return base_path / 'data' / 'input' / 'european' / 'parliament'


@pytest.fixture(scope='session')
def reference_european_parliament_path(base_path) -> Path:
    return base_path / 'data' / 'output' / 'european' / 'parliament'


@pytest.fixture(scope='session')
def voting_data_9_1_166077(data_european_parliament_path):
    tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="1", votingId="166077")

    data_file_path = data_european_parliament_path / f"votings_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def voting_data_9_1_166284(data_european_parliament_path):
    tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="1", votingId="166284")

    data_file_path = data_european_parliament_path / f"votings_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def voting_data_9_73_125262(data_european_parliament_path):
    tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="73", votingId="125262")

    data_file_path = data_european_parliament_path / f"votings_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def voting_data_9_154_141899(data_european_parliament_path):
    tag = VotingTag(chamberName="european-parliament", termId="9", sessionId="154", votingId="141899")

    data_file_path = data_european_parliament_path / f"votings_{tag.term_id}_{tag.session_id}_{tag.voting_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def group_data_grupa_renew_europe(data_european_parliament_path):
    tag = GroupTag(chamberName="european-parliament", termId="9", id="Grupa Renew Europe")

    data_file_path = data_european_parliament_path / f"groups_{tag.term_id}_{tag.id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def members_9_124807(data_european_parliament_path):
    tag = MemberTag(chamberName="european-parliament", termId="9", memberId="124807")

    data_file_path = data_european_parliament_path / f"members_{tag.term_id}_{tag.member_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def members_9_197612(data_european_parliament_path):
    tag = MemberTag(chamberName="european-parliament", termId="9", memberId="197612")

    data_file_path = data_european_parliament_path / f"members_{tag.term_id}_{tag.member_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def members_9_96752(data_european_parliament_path):
    tag = MemberTag(chamberName="european-parliament", termId="9", memberId="96752")

    data_file_path = data_european_parliament_path / f"members_{tag.term_id}_{tag.member_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def members_9_239973(data_european_parliament_path):
    tag = MemberTag(chamberName="european-parliament", termId="9", memberId="239973")

    data_file_path = data_european_parliament_path / f"members_{tag.term_id}_{tag.member_id}.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def statements_9_2024_03_12_10_5(data_european_parliament_path):
    tag = StatementTag(
        chamberName="european-parliament", termId="9", sessionId="9", dateId="2024-03-12", statementId="10-5")

    data_file_path = data_european_parliament_path / "statement_9_2024_03_12_10_5.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def statements_9_2024_03_12_12_9(data_european_parliament_path):
    tag = StatementTag(
        chamberName="european-parliament", termId="9", sessionId="9", dateId="2024-03-12", statementId="12-9")

    data_file_path = data_european_parliament_path / "statement_9_2024_03_12_12_9.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag


@pytest.fixture(scope='session')
def statements_9_2020_06_18_3_39(data_european_parliament_path):
    tag = StatementTag(
        chamberName="european-parliament", termId="9", sessionId="9", dateId="2020-06-18", statementId="3-38")

    data_file_path = data_european_parliament_path / "statement_9_2020_06_18_3_39.json"
    data = json.load(data_file_path.open(encoding='utf-8'))

    return data, tag
