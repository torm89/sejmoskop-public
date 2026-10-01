from sqlalchemy import func, and_, or_
from sqlalchemy import select, case, Integer, cast, Numeric

from processing.models.tags import TermTag, VotingOutcomeCall
from processing.transformers.analytics import AnalyticsTransformer

# The Sejmoskop app presents the European Parliament from a Polish perspective,
# so MEP rankings are restricted to Polish members (mirrors the DAO-level filter
# in models/dao/aws/s3/analytics/members.py). For sejm/senat all members are
# 'Polska', so this filter is a no-op there.
POLAND = 'Polska'

# A member needs at least this many divided votes (votes where their own club
# split) before their rebellion rate is stable enough to rank — otherwise a
# handful of votes produces noisy 0%/100% outliers. Tunable once we see the real
# distribution on dev.
MIN_DIVIDED_VOTINGS = 20


class MembersAnalyticsTransformer(AnalyticsTransformer):

    @staticmethod
    def members_groups_query(term_tag: TermTag, country=None):
        members_subquery = MembersAnalyticsTransformer.members_query(term_tag=term_tag, country=country).subquery()

        votings_normal_subquery = MembersAnalyticsTransformer.votings_normal_query(term_tag=term_tag).subquery()
        votings_outcomes_normal_subquery = MembersAnalyticsTransformer.votings_outcomes_normal_query(
            term_tag=term_tag).subquery()

        votings_outcomes_subquery_date = (
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

        votings_outcomes_subquery_numbers = (
            select(
                votings_outcomes_subquery_date,
                func
                .row_number()
                .over(
                    order_by=[
                        votings_outcomes_subquery_date.c.datetime.desc()
                    ],
                    partition_by=[
                        votings_outcomes_subquery_date.c.member_name,
                    ]
                ).label('number')
            )
            .subquery()
        )

        return (
            select(
                members_subquery,
                votings_outcomes_subquery_numbers.c.group_name_short,
            )
            .join(
                members_subquery,
                votings_outcomes_subquery_numbers.c.member_name == members_subquery.c.voting_name
            )
            .where(
                votings_outcomes_subquery_numbers.c.number == 1
            )
            .order_by(
                members_subquery.c.last_name,
                members_subquery.c.first_name,
            )
        )

    @staticmethod
    def members_voting_outcome_stats_query(term_tag: TermTag):
        members_subquery = MembersAnalyticsTransformer.members_query(term_tag=term_tag).subquery()
        votings_outcomes_normal_subquery = MembersAnalyticsTransformer.votings_outcomes_normal_query(
            term_tag=term_tag).subquery()

        return (
            select(
                members_subquery.c.member_id,
                members_subquery.c.country,
                votings_outcomes_normal_subquery.c.call,
                func.count(votings_outcomes_normal_subquery.c.call).label("count")
            )
            .join(
                members_subquery,
                members_subquery.c.voting_name == votings_outcomes_normal_subquery.c.member_name
            )
            .group_by(
                members_subquery.c.member_id,
                members_subquery.c.country,
                votings_outcomes_normal_subquery.c.call
            )
        )

    @staticmethod
    def _members_voting_outcome_call_ranking_query(term_tag: TermTag, call: str, country=POLAND):
        votings_outcomes_normal_subquery = MembersAnalyticsTransformer.votings_outcomes_normal_query(
            term_tag=term_tag).subquery()

        call_percent_subquery = (
            select(
                votings_outcomes_normal_subquery.c.member_name,
                (
                    cast(
                        1.0 * func.sum(
                            case((votings_outcomes_normal_subquery.c.call == call, 1), else_=0)) / func.count(),
                        Numeric(6, 4)
                    )
                ).label("percentage")
            )
            .group_by(
                votings_outcomes_normal_subquery.c.member_name,
            )
            .subquery()
        )

        members_groups_subquery = MembersAnalyticsTransformer.members_groups_query(term_tag=term_tag).subquery()

        if country:
            members_groups_subquery = (
                select(
                    members_groups_subquery
                )
                .where(
                    members_groups_subquery.c.country == country
                )
                .subquery()
            )

        return (
            select(
                members_groups_subquery.c.member_id,
                members_groups_subquery.c.first_name,
                members_groups_subquery.c.last_name,
                members_groups_subquery.c.member_type,
                members_groups_subquery.c.group_name_short,
                func.rank().over(
                    order_by=call_percent_subquery.c.percentage.desc(),
                )
                .label('rank'),
                call_percent_subquery.c.percentage
            )
            .join(
                call_percent_subquery,
                members_groups_subquery.c.voting_name == call_percent_subquery.c.member_name,
            )
            .order_by('rank')
        )

    @staticmethod
    def members_votings_outcomes_no_voted_ranking_query(term_tag: TermTag):
        return MembersAnalyticsTransformer._members_voting_outcome_call_ranking_query(
            term_tag=term_tag, call=VotingOutcomeCall.no_voted.value)

    @staticmethod
    def members_votings_outcomes_abstain_ranking_query(term_tag: TermTag):
        return MembersAnalyticsTransformer._members_voting_outcome_call_ranking_query(
            term_tag=term_tag, call=VotingOutcomeCall.abstain.value)

    @staticmethod
    def members_votings_outcomes_consistency_chamber_query(term_tag: TermTag):
        votings_normal_subquery = (
            MembersAnalyticsTransformer
            .votings_normal_with_session_id_voting_id_number_query(term_tag=term_tag).subquery())
        votings_outcomes_normal_subquery = (
            MembersAnalyticsTransformer.votings_outcomes_normal_query(term_tag=term_tag).subquery())

        chamber_decision_count_subquery = (
            select(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.call,
                func.count(votings_outcomes_normal_subquery.c.call).label("count")
            )
            .group_by(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.call,
            )
            .subquery()
        )

        chamber_decision_rank_subquery = (
            select(
                chamber_decision_count_subquery,
                func.rank().over(
                    order_by=chamber_decision_count_subquery.c.count.desc(),
                    partition_by=[
                        chamber_decision_count_subquery.c.session_id,
                        chamber_decision_count_subquery.c.voting_id
                    ]
                )
                .label('rank')
            )
            .subquery()
        )

        chamber_decision_subquery = (
            select(
                chamber_decision_rank_subquery
            )
            .where(
                chamber_decision_rank_subquery.c.rank == 1
            )
            .subquery()
        )

        votings_outcomes_chamber_decision_subquery = (
            select(
                votings_outcomes_normal_subquery,
                case(
                    (chamber_decision_subquery.c.call == votings_outcomes_normal_subquery.c.call, 1),
                    else_=0
                )
                .label("consistency")
            )
            .join(
                chamber_decision_subquery,
                and_(
                    votings_outcomes_normal_subquery.c.session_id == chamber_decision_subquery.c.session_id,
                    votings_outcomes_normal_subquery.c.voting_id == chamber_decision_subquery.c.voting_id
                ),
                isouter=True
            )
            .where(
                votings_outcomes_normal_subquery.c.call != VotingOutcomeCall.no_voted.value
            )
            .subquery()
        )

        votings_outcomes_chamber_decision_date_subquery = (
            select(
                votings_outcomes_chamber_decision_subquery,
                votings_normal_subquery.c.datetime
            )
            .join(
                votings_normal_subquery,
                and_(
                    votings_outcomes_chamber_decision_subquery.c.session_id == votings_normal_subquery.c.session_id,
                    votings_outcomes_chamber_decision_subquery.c.voting_id == votings_normal_subquery.c.voting_id
                )
            )
            .subquery()
        )

        # EP votings share a date-only datetime, so the rolling-average window
        # must order by datetime+voting_id (same key as the x-axis numbering in
        # votings_normal_with_session_id_voting_id_number_query) to stay
        # deterministic and aligned with the plotted sequence. sejm/senat keep
        # datetime-only ordering (distinct timestamps, no ties).
        window_order = [votings_outcomes_chamber_decision_date_subquery.c.datetime]
        if term_tag.chamber_name == 'european-parliament':
            window_order = [
                votings_outcomes_chamber_decision_date_subquery.c.datetime,
                votings_outcomes_chamber_decision_date_subquery.c.voting_id.cast(Integer),
            ]

        votings_outcomes_chamber_decision_average_subquery = (
            select(
                votings_outcomes_chamber_decision_date_subquery.c.member_name,
                votings_outcomes_chamber_decision_date_subquery.c.session_id,
                votings_outcomes_chamber_decision_date_subquery.c.voting_id,
                votings_outcomes_chamber_decision_date_subquery.c.datetime,
                func.avg(
                    votings_outcomes_chamber_decision_date_subquery.c.consistency
                )
                .over(
                    order_by=window_order,
                    partition_by=[
                        votings_outcomes_chamber_decision_date_subquery.c.member_name
                    ],
                    rows=(-19, 0)
                )
                .label('consistency_average_b20'),
                func.avg(
                    votings_outcomes_chamber_decision_date_subquery.c.consistency
                )
                .over(
                    order_by=window_order,
                    partition_by=[
                        votings_outcomes_chamber_decision_date_subquery.c.member_name
                    ],
                    rows=(-49, 0)
                )
                .label('consistency_average_b50'),
                func.avg(
                    votings_outcomes_chamber_decision_date_subquery.c.consistency
                )
                .over(
                    order_by=window_order,
                    partition_by=[
                        votings_outcomes_chamber_decision_date_subquery.c.member_name
                    ],
                    rows=(-99, 0)
                )
                .label('consistency_average_b100')
            )
            .subquery()
        )

        all_votings_outcomes_chamber_decision_average_subquery = (
            select(
                votings_outcomes_normal_subquery.c.member_name,
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_normal_subquery.c.datetime,
                votings_normal_subquery.c.session_id_number,
                votings_normal_subquery.c.voting_id_number,
                votings_outcomes_chamber_decision_average_subquery.c.consistency_average_b20,
                votings_outcomes_chamber_decision_average_subquery.c.consistency_average_b50,
                votings_outcomes_chamber_decision_average_subquery.c.consistency_average_b100,
            )
            .join(
                votings_outcomes_chamber_decision_average_subquery,
                and_(
                    votings_outcomes_normal_subquery.c.session_id == votings_outcomes_chamber_decision_average_subquery.c.session_id,
                    votings_outcomes_normal_subquery.c.voting_id == votings_outcomes_chamber_decision_average_subquery.c.voting_id,
                    votings_outcomes_normal_subquery.c.member_name == votings_outcomes_chamber_decision_average_subquery.c.member_name
                ),
                isouter=True
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

        members_subquery = MembersAnalyticsTransformer.members_query(term_tag=term_tag).subquery()

        q = (
            select(
                members_subquery.c.member_id,
                members_subquery.c.country,
                all_votings_outcomes_chamber_decision_average_subquery.c.session_id_number.label('session_id'),
                all_votings_outcomes_chamber_decision_average_subquery.c.voting_id_number.label('voting_id'),
                all_votings_outcomes_chamber_decision_average_subquery.c.datetime,
                all_votings_outcomes_chamber_decision_average_subquery.c.consistency_average_b20,
                all_votings_outcomes_chamber_decision_average_subquery.c.consistency_average_b50,
                all_votings_outcomes_chamber_decision_average_subquery.c.consistency_average_b100,
            )
            .join(
                all_votings_outcomes_chamber_decision_average_subquery,
                members_subquery.c.voting_name == all_votings_outcomes_chamber_decision_average_subquery.c.member_name
            )
            .order_by(
                members_subquery.c.member_id,
                all_votings_outcomes_chamber_decision_average_subquery.c.session_id_number,
                all_votings_outcomes_chamber_decision_average_subquery.c.voting_id_number
            )
        )

        return q

    @staticmethod
    def _votings_outcomes_group_decision_average_query(term_tag: TermTag):
        votings_outcomes_normal_subquery = MembersAnalyticsTransformer.votings_outcomes_normal_query(
            term_tag=term_tag).subquery()

        group_decision_count_subquery = (
            select(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.group_name_short,
                votings_outcomes_normal_subquery.c.call,
                func.count(votings_outcomes_normal_subquery.c.call).label("count")
            )
            .group_by(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.group_name_short,
                votings_outcomes_normal_subquery.c.call,
            )
            .subquery()
        )

        group_decision_rank_subquery = (
            select(
                group_decision_count_subquery,
                func.rank().over(
                    order_by=group_decision_count_subquery.c.count.desc(),
                    partition_by=[
                        group_decision_count_subquery.c.session_id,
                        group_decision_count_subquery.c.voting_id,
                        group_decision_count_subquery.c.group_name_short
                    ]
                )
                .label('rank')
            )
            .subquery()
        )

        group_decision_subquery = (
            select(
                group_decision_rank_subquery
            )
            .where(
                group_decision_rank_subquery.c.rank == 1
            )
            .subquery()
        )

        votings_outcomes_group_decision_subquery = (
            select(
                votings_outcomes_normal_subquery.c.session_id,
                votings_outcomes_normal_subquery.c.voting_id,
                votings_outcomes_normal_subquery.c.member_name,
                group_decision_subquery.c.group_name_short.label('group_reference'),
                case(
                    (group_decision_subquery.c.call == votings_outcomes_normal_subquery.c.call, 1),
                    else_=0
                )
                .label("consistency")
            )
            .join(
                group_decision_subquery,
                and_(
                    votings_outcomes_normal_subquery.c.session_id == group_decision_subquery.c.session_id,
                    votings_outcomes_normal_subquery.c.voting_id == group_decision_subquery.c.voting_id
                )
            )
            .where(
                or_(
                    votings_outcomes_normal_subquery.c.call != VotingOutcomeCall.no_voted.value,
                    group_decision_subquery.c.call == VotingOutcomeCall.no_voted.value,
                )
            )
            .subquery()
        )

        return (
            select(
                votings_outcomes_group_decision_subquery.c.member_name,
                votings_outcomes_group_decision_subquery.c.group_reference,
                func.avg(
                    votings_outcomes_group_decision_subquery.c.consistency
                )
                .label('consistency_average')
            )
            .group_by(
                votings_outcomes_group_decision_subquery.c.member_name,
                votings_outcomes_group_decision_subquery.c.group_reference,
            )
        )

    @staticmethod
    def members_votings_outcomes_consistency_groups_query(term_tag: TermTag):
        votings_outcomes_group_decision_average_subquery = (
            MembersAnalyticsTransformer._votings_outcomes_group_decision_average_query(
                term_tag=term_tag).subquery())

        members_subquery = MembersAnalyticsTransformer.members_query(term_tag=term_tag).subquery()
        groups_subquery = MembersAnalyticsTransformer.groups_query(term_tag=term_tag).subquery()

        q = (
            select(
                members_subquery.c.member_id,
                members_subquery.c.country,
                groups_subquery.c.name.label('group_reference_name'),
                votings_outcomes_group_decision_average_subquery.c.group_reference.label('group_reference_name_short'),
                votings_outcomes_group_decision_average_subquery.c.consistency_average
            )
            .join(
                votings_outcomes_group_decision_average_subquery,
                members_subquery.c.voting_name == votings_outcomes_group_decision_average_subquery.c.member_name
            )
            .join(
                groups_subquery,
                votings_outcomes_group_decision_average_subquery.c.group_reference == groups_subquery.c.name_short
            )
            .order_by(
                members_subquery.c.member_id,
                votings_outcomes_group_decision_average_subquery.c.group_reference
            )
        )

        return q

    @staticmethod
    def members_votings_outcomes_rebel_ranking_query(term_tag: TermTag, country=POLAND,
                                                     min_divided=MIN_DIVIDED_VOTINGS):
        member_rebellion_subquery = MembersAnalyticsTransformer.votings_outcomes_member_rebellion_query(
            term_tag=term_tag).subquery()

        rebellion_rate_subquery = (
            select(
                member_rebellion_subquery.c.member_name,
                member_rebellion_subquery.c.group_reference,
                func.count().label('divided_votings'),
                (
                    cast(
                        1.0 * func.sum(member_rebellion_subquery.c.rebelled) / func.count(),
                        Numeric(6, 4)
                    )
                ).label('percentage'),
            )
            .group_by(
                member_rebellion_subquery.c.member_name,
                member_rebellion_subquery.c.group_reference,
            )
            .subquery()
        )

        members_groups_subquery = MembersAnalyticsTransformer.members_groups_query(term_tag=term_tag).subquery()

        if country:
            members_groups_subquery = (
                select(
                    members_groups_subquery
                )
                .where(
                    members_groups_subquery.c.country == country
                )
                .subquery()
            )

        return (
            select(
                members_groups_subquery.c.member_id,
                members_groups_subquery.c.first_name,
                members_groups_subquery.c.last_name,
                members_groups_subquery.c.member_type,
                members_groups_subquery.c.group_name_short,
                func.rank().over(order_by=rebellion_rate_subquery.c.percentage.desc()).label('rank'),
                rebellion_rate_subquery.c.percentage,
            )
            .join(
                rebellion_rate_subquery,
                and_(
                    members_groups_subquery.c.voting_name == rebellion_rate_subquery.c.member_name,
                    members_groups_subquery.c.group_name_short == rebellion_rate_subquery.c.group_reference,
                )
            )
            .where(
                rebellion_rate_subquery.c.divided_votings >= min_divided
            )
            .order_by('rank')
        )
