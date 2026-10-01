from processing.models.tags import TermTag
from processing.transformers.analytics.voting import VotingRollCallAnalyticsTransformer

TERM_TAG = TermTag(chamberName="sejm", termId="10")
TERM_TAG_SENAT = TermTag(chamberName="senat", termId="10")
TERM_TAG_EP = TermTag(chamberName="european-parliament", termId="9")


def _sql(query):
    return str(query.compile(compile_kwargs={"literal_binds": True}))


def test_roll_call_maps_call_to_web_labels():
    sql = _sql(VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=TERM_TAG))

    assert "'YES'" in sql
    assert "'NO'" in sql
    assert "'ABSTAIN'" in sql
    assert "'ABSENT'" in sql


def test_roll_call_excludes_quorum():
    sql = _sql(VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=TERM_TAG))

    assert "stwierdzenie kworum" in sql


def test_roll_call_truncates_date_to_ten_chars():
    sql = _sql(VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=TERM_TAG))

    assert "substr" in sql.lower()
    assert ", 10" in sql


def test_roll_call_sejm_joins_members_by_member_id():
    # The Sejm captures a reliable MP id during voting processing, so the
    # member join keys off member_id (the voted name can differ from voting_name).
    sql = _sql(VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=TERM_TAG))

    assert "members.member_id = anon_1.member_id" in sql
    assert "members.voting_name" not in sql


def test_roll_call_senat_joins_members_by_voting_name():
    # The Senat leaves member_id empty, so the member join keys off the
    # canonical key: the voted member_name equals the member's voting_name.
    sql = _sql(VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=TERM_TAG_SENAT))

    assert "members.voting_name = anon_1.member_name" in sql


def test_roll_call_european_parliament_joins_members_by_voting_name():
    # The European Parliament also leaves member_id empty (the PersId rides in
    # member_name == voting_name), so it joins by voting_name like the Senat.
    sql = _sql(VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=TERM_TAG_EP))

    assert "members.voting_name = anon_1.member_name" in sql
