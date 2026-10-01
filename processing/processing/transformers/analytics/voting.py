from sqlalchemy import select, and_, case, func

from processing.models.tables.member import Member
from processing.models.tables.voting import Voting
from processing.models.tags import TermTag, VotingOutcomeCall
from processing.transformers.analytics import AnalyticsTransformer


class VotingRollCallAnalyticsTransformer:

    @staticmethod
    def voting_roll_call_query(term_tag: TermTag):
        # Reuse the proven normal-outcomes query: it is normal-only and already
        # drops the 'stwierdzenie kworum' votings (see transformers/analytics).
        outcomes = AnalyticsTransformer.votings_outcomes_normal_query(term_tag=term_tag).subquery()

        # Map the raw `call` to the four labels the web consumes. Must be
        # explicit for all four values: the web maps anything outside
        # YES/NO/ABSTAIN to ABSENT, so emitting raw yea/nay/abstain would
        # silently collapse every vote to ABSENT.
        vote = case(
            (outcomes.c.call == VotingOutcomeCall.yea.value, 'YES'),
            (outcomes.c.call == VotingOutcomeCall.nay.value, 'NO'),
            (outcomes.c.call == VotingOutcomeCall.abstain.value, 'ABSTAIN'),
            (outcomes.c.call == VotingOutcomeCall.no_voted.value, 'ABSENT'),
            else_='ABSENT',
        ).label('vote')

        # The lake stores datetime as a date plus time; the web shows only the
        # date, so truncate to YYYY-MM-DD here and keep the web a thin reader.
        date = func.substr(Voting.datetime, 1, 10).label('date')

        # Pick the member-join key by chamber. The Sejm captures a reliable MP
        # id in member_id during voting processing, so join by it (the voted
        # name there can differ from the member's voting_name). The Senat and
        # the European Parliament leave member_id empty, so use the canonical
        # key: the voted member_name equals the member's voting_name.
        if term_tag.chamber_name == 'sejm':
            member_join = Member.member_id == outcomes.c.member_id
        else:
            member_join = Member.voting_name == outcomes.c.member_name

        return (
            select(
                outcomes.c.session_id,
                outcomes.c.voting_id,
                # The web links member profiles by member_id, so emit the joined
                # member's real id; fall back to the raw voted name if unmatched.
                func.coalesce(Member.member_id, outcomes.c.member_name).label('member_id'),
                Member.first_name,
                Member.second_name,
                # Names come from the joined member; fall back to the raw voted
                # name if the member is somehow absent.
                func.coalesce(Member.last_name, outcomes.c.member_name).label('last_name'),
                outcomes.c.group_name_short,
                vote,
                date,
                Voting.description_01,
                Voting.description_02,
            )
            # LEFT join so the vote row survives even if the member is absent
            # (older terms, stray id, unresolved name).
            .join(
                Member,
                and_(
                    outcomes.c.chamber_name == Member.chamber_name,
                    outcomes.c.term_id == Member.term_id,
                    member_join,
                ),
                isouter=True,
            )
            .join(
                Voting,
                and_(
                    outcomes.c.chamber_name == Voting.chamber_name,
                    outcomes.c.term_id == Voting.term_id,
                    outcomes.c.session_id == Voting.session_id,
                    outcomes.c.voting_id == Voting.voting_id,
                ),
                isouter=True,
            )
            .order_by(
                outcomes.c.session_id,
                outcomes.c.voting_id,
            )
        )
