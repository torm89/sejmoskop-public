from sqlalchemy import select, func, Integer, and_, cast, Numeric

from processing.models.tags import TermTag
from processing.transformers.analytics import AnalyticsTransformer
from processing.transformers.analytics.members import POLAND

# Below this many distinct members a club is too small for a stable discipline
# rate (a single defector swings it wildly). Tunable once we see prod data.
MIN_CLUB_MEMBERS = 5


class GroupsAnalyticsTransformer(AnalyticsTransformer):

    @staticmethod
    def groups_members_diff_count_query(term_tag: TermTag):
        votings_normal_subquery = GroupsAnalyticsTransformer.votings_normal_query(term_tag=term_tag).subquery()
        votings_outcomes_normal_subquery = (
            GroupsAnalyticsTransformer
            .votings_outcomes_normal_query(
                term_tag=term_tag
            ).subquery()
        )

        votings_outcomes_normal_subquery = (
            select(
                votings_outcomes_normal_subquery,
                votings_normal_subquery.c.datetime
            )
            .join(
                votings_normal_subquery,
                and_(
                    votings_outcomes_normal_subquery.c.session_id == votings_normal_subquery.c.session_id,
                    votings_outcomes_normal_subquery.c.voting_id == votings_normal_subquery.c.voting_id
                )
            )
            .subquery()
        )

        groups_members_count_subquery = (
            select(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.group_name_short,
                votings_outcomes_normal_subquery.c.datetime,
                func.count().label('count')
            )
            .group_by(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.group_name_short,
                votings_outcomes_normal_subquery.c.datetime
            )
            .subquery()
        )

        groups_members_count_row_number_subquery = (
            select(
                groups_members_count_subquery,
                func
                .row_number()
                .over(
                    order_by=[
                        groups_members_count_subquery.c.datetime
                    ],
                    partition_by=[
                        groups_members_count_subquery.c.group_name_short,
                    ]
                ).label('row_number')
            )
            .subquery()
        )

        groups_members_count_initial_subquery = (
            select(
                groups_members_count_row_number_subquery
            )
            .where(
                groups_members_count_row_number_subquery.c.row_number == 1
            )
            .subquery()
        )

        groups_members_diff_subquery = (
            select(
                groups_members_count_subquery.c.datetime,
                groups_members_count_subquery.c.group_name_short,
                (groups_members_count_subquery.c.count - groups_members_count_initial_subquery.c.count).label("diff")
            )
            .join(
                groups_members_count_initial_subquery,
                groups_members_count_subquery.c.group_name_short == groups_members_count_initial_subquery.c.group_name_short,
            )
        )

        return groups_members_diff_subquery

    @staticmethod
    def groups_votings_outcomes_discipline_ranking_query(term_tag: TermTag, country=POLAND,
                                                         min_members=MIN_CLUB_MEMBERS):
        # Club-level twin of the rebels ranking: over the club's divided votes,
        # what share of its members' votes went against the club line. Higher =
        # less disciplined. Reuses the shared per-member rebellion computation.
        member_rebellion_subquery = (
            GroupsAnalyticsTransformer.votings_outcomes_member_rebellion_query(term_tag=term_tag).subquery())

        # Restrict to the chosen country's members. For sejm/senat everyone is
        # 'Polska' so this is a no-op; for the EP it keeps the ranking to Polish
        # MEPs, matching the rest of the app (the line itself is still read from
        # the whole political group inside the shared rebellion query).
        members_subquery = GroupsAnalyticsTransformer.members_query(term_tag=term_tag, country=country).subquery()

        club_rebellion_subquery = (
            select(
                member_rebellion_subquery.c.group_reference.label('group_name_short'),
                (
                    cast(
                        1.0 * func.sum(member_rebellion_subquery.c.rebelled) / func.count(),
                        Numeric(6, 4)
                    )
                ).label("percentage")
            )
            .join(
                members_subquery,
                members_subquery.c.voting_name == member_rebellion_subquery.c.member_name
            )
            .group_by(
                member_rebellion_subquery.c.group_reference,
            )
            .having(
                func.count(func.distinct(member_rebellion_subquery.c.member_name)) >= min_members
            )
            .subquery()
        )

        return (
            select(
                club_rebellion_subquery.c.group_name_short,
                func.rank().over(
                    order_by=club_rebellion_subquery.c.percentage.desc(),
                )
                .label('rank'),
                club_rebellion_subquery.c.percentage
            )
            .order_by('rank')
        )
