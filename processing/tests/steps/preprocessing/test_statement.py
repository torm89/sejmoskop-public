import json

from botocore.exceptions import ClientError as BotoClientError

from processing.models.tags import StatementTag
from processing.transformers.processing.sejm.statement import StatementProcessingTransformerSejm


def test_extract_timeline(statements_data_path, true_data_path):
    proceedings = json.load((statements_data_path / 'sejm_10_1_3_000.json').open('rb'))

    tag = StatementTag(chamberName="sejm", termId="10", sessionId="1", dateId="3", statementId="0")

    class FakeDao:
        def get(self, tag: StatementTag):
            return json.load((statements_data_path / f'sejm_10_1_3_{tag.statement_id.zfill(3)}.json').open('rb'))

    timeline = StatementProcessingTransformerSejm.extract_statements(
        tag=tag, proceedings=proceedings, hot_dao=FakeDao())

    # print(json.dump(timeline, (true_data_path / 'sejm_10_1_3_timeline.json').open('w'), indent=2))

    assert timeline == json.load((true_data_path / 'sejm_10_1_3_timeline.json').open('rb'))

    # The one contribution submitted in writing is flagged at document level,
    # unified with the European Parliament's is_written.
    assert [statement['is_written'] for statement in timeline] == \
           [False, True, False, False, False, False, False]


def test_extract_timeline_skips_linked_statement_that_was_never_scraped(statements_data_path, true_data_path):
    proceedings = json.load((statements_data_path / 'sejm_10_1_3_000.json').open('rb'))

    tag = StatementTag(chamberName="sejm", termId="10", sessionId="1", dateId="3", statementId="0")

    class FakeDao:
        def get(self, tag: StatementTag):
            if tag.statement_id == '3':
                raise BotoClientError({'Error': {'Code': 'NoSuchKey'}}, 'GetObject')
            return json.load((statements_data_path / f'sejm_10_1_3_{tag.statement_id.zfill(3)}.json').open('rb'))

    timeline = StatementProcessingTransformerSejm.extract_statements(
        tag=tag, proceedings=proceedings, hot_dao=FakeDao())

    expected = json.load((true_data_path / 'sejm_10_1_3_timeline.json').open('rb'))
    expected = [statement for statement in expected if statement['tag']['statementId'] != '3']
    for i, statement in enumerate(expected):
        statement['tag']['statementIdNew'] = i

    assert timeline == expected
