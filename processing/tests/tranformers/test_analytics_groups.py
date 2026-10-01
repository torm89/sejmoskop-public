from processing.models.tags import TermTag
from processing.transformers.analytics.groups import GroupsAnalyticsTransformer
from processing.transformers.analytics.members import POLAND

TERM_TAG = TermTag(chamberName="european-parliament", termId="9")


def _sql(query):
    return str(query.compile(compile_kwargs={"literal_binds": True}))


def test_discipline_ranking_defaults_to_poland_only():
    sql = _sql(GroupsAnalyticsTransformer.groups_votings_outcomes_discipline_ranking_query(term_tag=TERM_TAG))

    assert f"= '{POLAND}'" in sql


def test_discipline_ranking_without_country_has_no_country_filter():
    sql = _sql(GroupsAnalyticsTransformer.groups_votings_outcomes_discipline_ranking_query(
        term_tag=TERM_TAG, country=None))

    assert POLAND not in sql
