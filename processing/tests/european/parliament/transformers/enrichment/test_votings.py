from processing.models.tags import TermTag
from processing.transformers.enrichment.votings import (
    DUMMY_GROUP_NAME_SHORT,
    MemberVotingOutcomeDummyGroupNameShortEnrichmentTransformerEuropeanParliament as DummyGroupTransformer,
)

TERM_TAG = TermTag(chamberName="european-parliament", termId="9")


def _sql(query):
    return str(query.compile(compile_kwargs={"literal_binds": True}))


def test_member_voting_names_has_no_cartesian_join():
    # Regression guard: the filter and distinct must reference the
    # votings-outcomes subquery, not the raw VotingOutcome table. Referencing
    # the raw table pulled "votings-outcomes" into the FROM clause a second
    # time, producing a cartesian product that returned every member name.
    query = DummyGroupTransformer.member_voting_names(term_tag=TERM_TAG)

    assert len(query.get_final_froms()) == 1


def test_member_voting_names_filters_dummy_group_and_is_distinct():
    query = DummyGroupTransformer.member_voting_names(term_tag=TERM_TAG)
    sql = _sql(query)

    assert "SELECT DISTINCT" in sql
    assert DUMMY_GROUP_NAME_SHORT in sql
