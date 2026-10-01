from sqlalchemy import select, Integer, func, sql, and_, case

from processing.models.tables.group import Group
from processing.models.tables.member import Member
from processing.models.tables.statement import Statement
from processing.models.tables.voting import Voting, VotingOutcomeNormal, VotingNormal
from processing.models.tags import TermTag, VotingOutcomeCall


class AnalyticsTransformer:

    @staticmethod
    def members_query(term_tag: TermTag, country=None):
        query = (
            select(Member)
            .where(
                Member.chamber_name == term_tag.chamber_name,
                Member.term_id == term_tag.term_id,
            )
        )

        if country:
            query = query.where(Member.country == country)

        return query.order_by(Member.member_id.cast(Integer))

    @staticmethod
    def votings_normal_query(term_tag: TermTag):
        return (
            select(VotingNormal)
            .where(
                Voting.chamber_name == term_tag.chamber_name,
                Voting.term_id == term_tag.term_id,
                Voting.description_02 != 'stwierdzenie kworum'
            )
        )

    @staticmethod
    def votings_normal_with_session_id_voting_id_number_query(term_tag: TermTag):
        votings_subquery = AnalyticsTransformer.votings_normal_query(term_tag=term_tag).subquery()

        votings_session_id_subquery = (
            select(
                votings_subquery.c.session_id,
                func.max(votings_subquery.c.datetime).label('datetime')
            )
            .group_by(votings_subquery.c.session_id)
            .subquery()
        )
        votings_session_id_number_subquery = (
            select(
                votings_session_id_subquery.c.session_id,
                func.row_number().over(order_by=votings_session_id_subquery.c.datetime).label('session_id_number')
            )
            .subquery()
        )

        votings_voting_id_subquery = (
            select(
                votings_subquery.c.session_id,
                votings_subquery.c.voting_id,
                func.max(votings_subquery.c.datetime).label('datetime')
            )
            .group_by(votings_subquery.c.session_id, votings_subquery.c.voting_id)
            .subquery()
        )
        # European Parliament votings carry a date-only datetime (every vote on a
        # session day collapses to T00:00:00), so ordering by datetime alone
        # breaks intra-day ties arbitrarily. Add voting_id as a deterministic,
        # chronological tiebreaker so the per-vote sequence is stable. sejm/senat
        # keep their original datetime-only ordering (distinct timestamps).
        voting_id_order = [votings_voting_id_subquery.c.datetime]
        if term_tag.chamber_name == 'european-parliament':
            voting_id_order.append(votings_voting_id_subquery.c.voting_id.cast(Integer))

        votings_voting_id_number_subquery = (
            select(
                votings_voting_id_subquery.c.session_id,
                votings_voting_id_subquery.c.voting_id,
                func.row_number().over(
                    order_by=voting_id_order,
                    partition_by=[votings_voting_id_subquery.c.session_id]
                ).label('voting_id_number')
            )
            .subquery()
        )

        return (
            select(
                votings_subquery,
                votings_session_id_number_subquery.c.session_id_number,
                votings_voting_id_number_subquery.c.voting_id_number
            )
            .join(
                votings_session_id_number_subquery,
                votings_subquery.c.session_id == votings_session_id_number_subquery.c.session_id
            )
            .join(
                votings_voting_id_number_subquery,
                and_(
                    votings_subquery.c.session_id == votings_voting_id_number_subquery.c.session_id,
                    votings_subquery.c.voting_id == votings_voting_id_number_subquery.c.voting_id
                )
            )
        )

    @staticmethod
    def votings_outcomes_normal_all_query(term_tag: TermTag):
        return (
            select(VotingOutcomeNormal)
            .where(
                VotingOutcomeNormal.chamber_name == term_tag.chamber_name,
                VotingOutcomeNormal.term_id == term_tag.term_id,
            )
        )

    @classmethod
    def votings_outcomes_normal_query(cls, term_tag: TermTag):
        return (
            cls.votings_outcomes_normal_all_query(term_tag=term_tag)
            .join(VotingOutcomeNormal.voting)
            .where(
                VotingNormal.description_02 != 'stwierdzenie kworum'
            )
        )

    @classmethod
    def votings_outcomes_member_rebellion_query(cls, term_tag: TermTag):
        # For every present member on a vote where their club splits (the present
        # members do not all pick the same call), flag whether they voted against
        # the club's line. Shared by the member rebels ranking and the club
        # discipline ranking. An absence (no_voted) is not a position, so it
        # neither makes a club look divided nor counts as a rebellion.
        votings_outcomes_normal_subquery = cls.votings_outcomes_normal_query(term_tag=term_tag).subquery()

        present_subquery = (
            select(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.group_name_short,
                votings_outcomes_normal_subquery.c.member_name,
                votings_outcomes_normal_subquery.c.call,
            )
            .where(
                votings_outcomes_normal_subquery.c.call != VotingOutcomeCall.no_voted.value
            )
            .subquery()
        )

        # How many present members of each club cast each call, per vote.
        call_count_subquery = (
            select(
                present_subquery.c.session_id,
                present_subquery.c.voting_id,
                present_subquery.c.group_name_short,
                present_subquery.c.call,
                func.count().label('count'),
            )
            .group_by(
                present_subquery.c.session_id,
                present_subquery.c.voting_id,
                present_subquery.c.group_name_short,
                present_subquery.c.call,
            )
            .subquery()
        )

        # Per (vote, club): rank calls to pick the line, plus the present total and
        # the top call's count, so we can tell whether the club actually split.
        call_window_subquery = (
            select(
                call_count_subquery.c.session_id,
                call_count_subquery.c.voting_id,
                call_count_subquery.c.group_name_short,
                call_count_subquery.c.call,
                func.rank().over(
                    order_by=[call_count_subquery.c.count.desc(), call_count_subquery.c.call],
                    partition_by=[
                        call_count_subquery.c.session_id,
                        call_count_subquery.c.voting_id,
                        call_count_subquery.c.group_name_short,
                    ],
                ).label('rank'),
                func.sum(call_count_subquery.c.count).over(
                    partition_by=[
                        call_count_subquery.c.session_id,
                        call_count_subquery.c.voting_id,
                        call_count_subquery.c.group_name_short,
                    ],
                ).label('present_total'),
                func.max(call_count_subquery.c.count).over(
                    partition_by=[
                        call_count_subquery.c.session_id,
                        call_count_subquery.c.voting_id,
                        call_count_subquery.c.group_name_short,
                    ],
                ).label('top_count'),
            )
            .subquery()
        )

        group_line_subquery = (
            select(
                call_window_subquery.c.session_id,
                call_window_subquery.c.voting_id,
                call_window_subquery.c.group_name_short,
                call_window_subquery.c.call.label('line'),
                call_window_subquery.c.present_total,
                call_window_subquery.c.top_count,
            )
            .where(
                call_window_subquery.c.rank == 1
            )
            .subquery()
        )

        return (
            select(
                present_subquery.c.member_name,
                present_subquery.c.group_name_short.label('group_reference'),
                case(
                    (present_subquery.c.call != group_line_subquery.c.line, 1),
                    else_=0
                ).label('rebelled'),
            )
            .join(
                group_line_subquery,
                and_(
                    present_subquery.c.session_id == group_line_subquery.c.session_id,
                    present_subquery.c.voting_id == group_line_subquery.c.voting_id,
                    present_subquery.c.group_name_short == group_line_subquery.c.group_name_short,
                )
            )
            .where(
                group_line_subquery.c.present_total > group_line_subquery.c.top_count
            )
        )

    @staticmethod
    def _groups_query_normal(term_tag: TermTag):
        return (
            select(Group)
            .where(
                Group.chamber_name == term_tag.chamber_name,
                Group.term_id == term_tag.term_id,
            )
        )

    @staticmethod
    def _groups_query_from_votings(term_tag: TermTag):
        votings_normal_subquery = AnalyticsTransformer.votings_normal_query(term_tag=term_tag).subquery()
        votings_outcomes_normal_subquery = (
            AnalyticsTransformer.votings_outcomes_normal_query(term_tag=term_tag).subquery())

        votings_normal_row_number_subquery = (
            select(
                votings_normal_subquery,
                func
                .row_number()
                .over(
                    order_by=[
                        votings_normal_subquery.c.session_id.cast(Integer).desc(),
                        votings_normal_subquery.c.voting_id.cast(Integer).desc(),
                    ],
                ).label('row_number')
            )
            .subquery()
        )

        votings_normal_last_subquery = (
            select(
                votings_normal_row_number_subquery
            )
            .where(
                votings_normal_row_number_subquery.c.row_number == 1
            )
            .subquery()
        )

        votings_outcomes_normal_last_subquery = (
            select(
                votings_normal_last_subquery,
                votings_outcomes_normal_subquery
            )
            .join(
                votings_outcomes_normal_subquery,
                and_(
                    votings_outcomes_normal_subquery.c.session_id == votings_normal_last_subquery.c.session_id,
                    votings_outcomes_normal_subquery.c.voting_id == votings_normal_last_subquery.c.voting_id
                ),
                isouter=True
            )
            .subquery()
        )

        return (
            select(
                sql.expression.literal_column("''").label("name"),
                votings_outcomes_normal_last_subquery.c.group_name_short.label("name_short"),
                sql.expression.literal_column("''").label("group_type"),
                votings_outcomes_normal_last_subquery.c.chamber_name,
                votings_outcomes_normal_last_subquery.c.term_id,
            )
            .distinct(
                votings_outcomes_normal_last_subquery.c.group_name_short,
            )
        )

    @staticmethod
    def groups_query(term_tag: TermTag):
        if term_tag.chamber_name == 'sejm' and term_tag.term_id in ['3', '4', '5', '6']:
            return AnalyticsTransformer._groups_query_from_votings(term_tag=term_tag)

        return AnalyticsTransformer._groups_query_normal(term_tag=term_tag)

    @staticmethod
    def statements_query(term_tag: TermTag):
        return (
            select(
                Statement, Statement.term_id.cast(Integer),
                Statement.date_id.cast(Integer),
                Statement.statement_id_new.cast(Integer)
            )
            .where(
                Statement.chamber_name == term_tag.chamber_name,
                Statement.term_id == term_tag.term_id,
                Statement.session_id.isnot(None),
                Statement.date_id.isnot(None),
                Statement.date != '01-01-1900'
            )
            .order_by(
                Statement.session_id.cast(Integer),
                Statement.date_id.cast(Integer),
                Statement.statement_id_new.cast(Integer)
            )
        )
