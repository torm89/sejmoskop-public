import json
from unittest.mock import patch, MagicMock

import pandas as pd

from processing.models.tags import TermTag, MemberTag
from processing.steps.enrichment.european.parliament.voting import \
    MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament


@patch.object(MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament, '_members_voting_outcomes_df')
def test_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_run(
        mock_members_voting_outcomes_df,
        fake_members_with_dummy_group_name_short_9_df,
        reference_european_parliament_steps_enrichment_path
):
    mock_members_voting_outcomes_df.return_value = fake_members_with_dummy_group_name_short_9_df

    step = MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament()

    step_payload = {
        'term_tag': TermTag(chamberName="european-parliament", termId="9"),
    }
    step_output = step._step_run(step_payload)
    changes_by_tag = step_output["group_name_short_changes"]
    step_output_serialized = [{k.model_dump_json(by_alias=True): v} for k, v in changes_by_tag.items()]

    reference_data_dict_path = reference_european_parliament_steps_enrichment_path / "member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_101039.json"
    # reference_data_dict_path.open('w+').write(json.dumps(step_output_serialized, indent=4))

    assert step_output_serialized[:100] == json.load(reference_data_dict_path.open(encoding='utf-8'))[:100]


def test_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_save_payload(
        fake_voting_outcome_data_9_1_166038,
        fake_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_166038,
        reference_european_parliament_steps_enrichment_path
):
    repository = MagicMock()
    repository.fetch_voting_outcome_data.return_value = fake_voting_outcome_data_9_1_166038
    repository.save = MagicMock()

    step = MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament()

    changes_by_tag = fake_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_166038
    step_payload = {"group_name_short_changes": changes_by_tag}
    step._step_save_payload(step_payload, repository=repository)

    assert repository.save.call_count == len(changes_by_tag)

    reference_data_dict_path = reference_european_parliament_steps_enrichment_path / "voting_outcomes_9_1_166038.json"
    # reference_data_dict_path.open('w+').write(
    #     json.dumps({
    #         "tag": repository.save.call_args_list[0][0][0].tag,
    #         "data": repository.save.call_args_list[0][0][0].df.to_dict(orient="records")
    #     }, indent=4)
    # )
    reference_data = json.load(reference_data_dict_path.open(encoding='utf-8'))

    assert repository.save.call_args_list[0][0][0].tag == reference_data['tag']
    pd.testing.assert_frame_equal(repository.save.call_args_list[0][0][0].df, pd.DataFrame(reference_data['data']))


def test_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_save_payload_ignores_term_tag(
        fake_voting_outcome_data_9_1_166038,
        fake_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_166038,
):
    repository = MagicMock()
    repository.fetch_voting_outcome_data.return_value = fake_voting_outcome_data_9_1_166038
    repository.save = MagicMock()

    step = MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament()

    # run() leaves a "term_tag" entry in the payload next to the changes; saving
    # reads only "group_name_short_changes", so term_tag must not interfere.
    changes_by_tag = fake_member_voting_outcome_group_name_short_enrichment_step_european_parliament_step_output_9_166038
    step_payload = {
        "group_name_short_changes": changes_by_tag,
        "term_tag": TermTag(chamberName="european-parliament", termId="9"),
    }

    step._step_save_payload(step_payload, repository=repository)

    assert repository.save.call_count == len(changes_by_tag)
