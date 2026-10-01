import datetime
import json
from unittest.mock import patch

from processing.models.tags import TermTag
from processing.steps.enrichment.european.parliament.voting import \
    VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament


@patch.object(VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament, '_members')
def test_voting_outcome_no_member_name_enrichment_step_european_parliament_member_voting_name_from_member_table(
        mocked_members,
        voting_processing_step_european_parliament_voting_data_9_73_125262, members_table_date_9_166277,
        reference_european_parliament_steps_enrichment_path
):
    mocked_members.return_value = members_table_date_9_166277

    step = VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament()

    term_tag = TermTag(chamberName="european-parliament", termId="9")
    member_voting_name = step._member_voting_name_from_member_table(
        term_tag=term_tag, member_name="Bourgeois", session=None)

    assert member_voting_name == "197467"


@patch.object(VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament, '_members')
def test_voting_outcome_no_member_name_enrichment_step_european_parliament_step_run(
        mocked_members,
        voting_processing_step_european_parliament_voting_data_9_73_125262, members_table_date_9_166277,
        reference_european_parliament_steps_enrichment_path
):
    mocked_members.return_value = members_table_date_9_166277

    data = voting_processing_step_european_parliament_voting_data_9_73_125262
    payload = {
        'voting_tag': data['voting_tag'],
        'voting_outcome_data': data['voting_outcome_data'],
    }

    step = VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament()
    payload = step._step_run(payload)

    voting_outcome_data_dict = payload['voting_outcome_data'].df_dict()

    reference_data_dict_path = reference_european_parliament_steps_enrichment_path / "voting_outcome_no_member_name_enrichment_step_european_parliament_step_run_9_1_166284.json"
    # reference_data_dict_path.open('w+').write(json.dumps(voting_outcome_data_dict, indent=4))

    assert voting_outcome_data_dict == json.load(reference_data_dict_path.open(encoding='utf-8'))
