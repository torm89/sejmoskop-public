import datetime
import json
from unittest.mock import patch

from processing.models.tags import TermTag
from processing.steps.enrichment.european.parliament.voting import \
    VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament


@patch.object(VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament, '_members')
def test_voting_outcome_no_voted_call_enrichment_step_european_parliament_member_ids_at_date(
        mocked_members,
        voting_processing_step_european_parliament_voting_data_9_1_166284, members_table_date_9_166277,
        reference_european_parliament_steps_enrichment_path
):
    mocked_members.return_value = members_table_date_9_166277

    step = VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament()

    term_tag = TermTag(chamberName="european-parliament", termId="9")
    member_ids_at_date = step._member_ids_at_date(term_tag=term_tag, date=datetime.date(2023, 3, 12), session=None)

    reference_data_dict_path = reference_european_parliament_steps_enrichment_path / "voting_outcome_no_voted_call_enrichment_step_european_parliament_member_ids_at_date_9_2023_03_12.json"
    # reference_data_dict_path.open('w+').write(json.dumps(member_ids_at_date, indent=4))

    assert member_ids_at_date == json.load(reference_data_dict_path.open(encoding='utf-8'))


@patch.object(VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament, '_members')
def test_voting_outcome_no_voted_call_enrichment_step_european_parliament_step_run(
        mocked_members,
        voting_processing_step_european_parliament_voting_data_9_1_166284, members_table_date_9_166277,
        reference_european_parliament_steps_enrichment_path
):
    mocked_members.return_value = members_table_date_9_166277

    data = voting_processing_step_european_parliament_voting_data_9_1_166284
    payload = {
        'voting_tag': data['voting_tag'],
        'voting_data': data['voting_data'],
        'voting_outcome_data': data['voting_outcome_data'],
    }

    step = VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament()
    payload = step._step_run(payload)

    voting_data_dict = payload['voting_data'].df_dict()
    voting_outcome_data_dict = payload['voting_outcome_data'].df_dict()

    reference_data_dict_path = reference_european_parliament_steps_enrichment_path / "voting_outcome_no_voted_call_enrichment_step_european_parliament_9_1_166284.json"
    # reference_data_dict_path.open('w+').write(
    #     json.dumps({
    #         'voting_data_dict': voting_data_dict,
    #         'voting_outcome_data_dict': voting_outcome_data_dict,
    #     }, indent=4)
    # )

    assert voting_outcome_data_dict == \
           json.load(reference_data_dict_path.open(encoding='utf-8'))['voting_outcome_data_dict']
