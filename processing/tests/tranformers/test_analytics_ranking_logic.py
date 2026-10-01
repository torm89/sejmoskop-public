"""Behavioural tests for the Phase 1 leaderboard queries.

Unlike the other analytics tests (which only compile the SQL and assert on the
Poland filter), these seed a tiny in-memory SQLite dataset, run the actual
queries and assert on the produced ranking. This is the only coverage for the
genuinely new logic: the rebellion rate measured **only on divided votes**, both
per member and aggregated per club (the discipline ranking).

The dataset (sejm/10, everyone 'Polska' so the country filter is a no-op):

  Club A: M1, M2, M3, M4        Club B: M5, M6
  5 votings, one session. Calls per vote (no_voted = absent):

    v1: A all 'for'                 (unanimous)   | B: M5 for,  M6 absent
    v2: A for/for/against/for       (divided)     | B: M5 for,  M6 absent
    v3: A for/against/against/against (divided)   | B: both against
    v4: A absent/for/against/for    (divided)     | B: both against
    v5: A all 'against'             (unanimous)   | B: both for

  Divided club-A votes are v2, v3, v4 (v1 and v5 are unanimous, so they carry no
  loyalty signal and must be ignored). On those, against the club line:
    M1 = 1/2 = 0.5   (rebels on v3; absent on v4, so only 2 divided votes count)
    M2 = 0/3 = 0.0
    M3 = 2/3
    M4 = 0/3 = 0.0
  Club B never splits among present members -> no rebellion rows at all.

  Club discipline (club A): 3 divided votes -> 11 present member-votes, 3 against
  the line -> rebellion rate 3/11. Club B has no divided votes, so it does not
  appear.
"""
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from processing.models.tables import Base
from processing.models.tables.member import Member
from processing.models.tables.voting import VotingNormal, VotingOutcomeNormal
from processing.models.tags import TermTag
from processing.transformers.analytics.groups import GroupsAnalyticsTransformer
from processing.transformers.analytics.members import MembersAnalyticsTransformer

TERM_TAG = TermTag(chamberName="sejm", termId="10")

# (member_name, member_id, group) for each seeded member.
MEMBERS = [
    ("M1", "1", "A"), ("M2", "2", "A"), ("M3", "3", "A"), ("M4", "4", "A"),
    ("M5", "5", "B"), ("M6", "6", "B"),
]

_NV = "no_voted"

# call per voting, keyed by member_name.
CALLS = {
    "1": {"M1": "for", "M2": "for", "M3": "for", "M4": "for", "M5": "for", "M6": _NV},
    "2": {"M1": "for", "M2": "for", "M3": "against", "M4": "for", "M5": "for", "M6": _NV},
    "3": {"M1": "for", "M2": "against", "M3": "against", "M4": "against", "M5": "against", "M6": "against"},
    "4": {"M1": _NV, "M2": "for", "M3": "against", "M4": "for", "M5": "against", "M6": "against"},
    "5": {"M1": "against", "M2": "against", "M3": "against", "M4": "against", "M5": "for", "M6": "for"},
}

GROUP_OF = {name: group for name, _, group in MEMBERS}
ID_OF = {name: member_id for name, member_id, _ in MEMBERS}


def _member(name, member_id):
    return Member(
        member_id=member_id, first_name="F", second_name="", last_name=name,
        member_type="active", voting_name=name, birth_date="", former_details="",
        country="Polska", chamber_name="sejm", term_id="10",
    )


def _voting(voting_id):
    return VotingNormal(
        chamber_name="sejm", term_id="10", session_id="1", voting_id=voting_id,
        datetime=f"2024-01-0{voting_id}T10:00:00", description_01="", description_02="",
    )


def _outcome(voting_id, name, call):
    return VotingOutcomeNormal(
        chamber_name="sejm", term_id="10", session_id="1", voting_id=voting_id,
        member_name=name, member_id=ID_OF[name], group_name_short=GROUP_OF[name], call=call,
    )


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([_member(name, member_id) for name, member_id, _ in MEMBERS])
        session.add_all([_voting(voting_id) for voting_id in CALLS])
        session.add_all([
            _outcome(voting_id, name, call)
            for voting_id, calls in CALLS.items()
            for name, call in calls.items()
        ])
        session.commit()
        yield session


def test_rebel_ranking_counts_only_divided_votes(session):
    query = MembersAnalyticsTransformer.members_votings_outcomes_rebel_ranking_query(
        term_tag=TERM_TAG, min_divided=1)
    df = pd.read_sql_query(query, session.connection())

    percentage = dict(zip(df.member_id, df.percentage))
    # M1 = 0.5: unanimous v1/v5 are ignored (else 0.25) and the absence on the
    # divided v4 is skipped (else 1/3), leaving exactly 1 rebellion in 2 votes.
    assert percentage["1"] == pytest.approx(0.5)
    assert percentage["2"] == pytest.approx(0.0)
    assert percentage["3"] == pytest.approx(round(2 / 3, 4))
    assert percentage["4"] == pytest.approx(0.0)
    # Club B never splits among present members -> nobody from B is ranked.
    assert "5" not in percentage and "6" not in percentage

    ordered = df.sort_values("rank")
    assert ordered.iloc[0].member_id == "3"  # biggest rebel first
    assert list(ordered.percentage) == sorted(ordered.percentage, reverse=True)


def test_rebel_ranking_drops_members_below_divided_threshold(session):
    query = MembersAnalyticsTransformer.members_votings_outcomes_rebel_ranking_query(
        term_tag=TERM_TAG, min_divided=3)
    df = pd.read_sql_query(query, session.connection())

    ranked = set(df.member_id)
    # M1 only has 2 divided votes (absent on the third) -> below the threshold.
    assert "1" not in ranked
    assert {"2", "3", "4"} <= ranked


def test_club_discipline_ranks_clubs_by_rebellion_rate(session):
    query = GroupsAnalyticsTransformer.groups_votings_outcomes_discipline_ranking_query(
        term_tag=TERM_TAG, min_members=1)
    df = pd.read_sql_query(query, session.connection())

    percentage = dict(zip(df.group_name_short, df.percentage))
    # Club A's 3 divided votes give 11 present member-votes, 3 against the line.
    assert percentage["A"] == pytest.approx(round(3 / 11, 4))
    # Club B never splits among present members -> no discipline signal.
    assert "B" not in percentage
    assert df.sort_values("rank").iloc[0].group_name_short == "A"


def test_club_discipline_drops_clubs_below_member_threshold(session):
    # Club A has 4 members; with the bar at 5 it is filtered out and nothing ranks.
    query = GroupsAnalyticsTransformer.groups_votings_outcomes_discipline_ranking_query(
        term_tag=TERM_TAG, min_members=5)
    df = pd.read_sql_query(query, session.connection())

    assert "A" not in set(df.group_name_short)
