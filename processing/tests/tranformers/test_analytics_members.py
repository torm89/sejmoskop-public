from processing.models.tags import TermTag
from processing.transformers.analytics.members import MembersAnalyticsTransformer, POLAND

TERM_TAG = TermTag(chamberName="european-parliament", termId="9")


def _sql(query):
    return str(query.compile(compile_kwargs={"literal_binds": True}))


def test_no_voted_ranking_defaults_to_poland_only():
    sql = _sql(MembersAnalyticsTransformer.members_votings_outcomes_no_voted_ranking_query(term_tag=TERM_TAG))

    assert f"= '{POLAND}'" in sql


def test_abstain_ranking_defaults_to_poland_only():
    sql = _sql(MembersAnalyticsTransformer.members_votings_outcomes_abstain_ranking_query(term_tag=TERM_TAG))

    assert f"= '{POLAND}'" in sql


def test_rebel_ranking_defaults_to_poland_only():
    sql = _sql(MembersAnalyticsTransformer.members_votings_outcomes_rebel_ranking_query(term_tag=TERM_TAG))

    assert f"= '{POLAND}'" in sql


def test_rebel_ranking_without_country_has_no_country_filter():
    sql = _sql(MembersAnalyticsTransformer.members_votings_outcomes_rebel_ranking_query(
        term_tag=TERM_TAG, country=None))

    assert POLAND not in sql


def test_ranking_without_country_has_no_country_filter():
    sql = _sql(MembersAnalyticsTransformer._members_voting_outcome_call_ranking_query(
        term_tag=TERM_TAG, call="no_voted", country=None))

    assert POLAND not in sql
