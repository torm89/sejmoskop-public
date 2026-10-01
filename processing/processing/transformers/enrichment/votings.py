from sqlalchemy import Integer, select

from processing.models.tags import TermTag
from processing.transformers.analytics import AnalyticsTransformer

DUMMY_GROUP_NAME_SHORT = '???'


class VotingOutcomeNoMemberNameEnrichmentTransformerEuropeanParliament:
    @classmethod
    def members_query(cls, term_tag: TermTag):
        return AnalyticsTransformer.members_query(term_tag=term_tag)


class VotingOutcomeNoVotedCallEnrichmentTransformerEuropeanParliament:
    @classmethod
    def members_query(cls, term_tag: TermTag):
        return AnalyticsTransformer.members_query(term_tag=term_tag)


class MemberVotingOutcomeDummyGroupNameShortEnrichmentTransformerEuropeanParliament:

    @classmethod
    def member_voting_names(cls, term_tag: TermTag):
        votings_outcomes = AnalyticsTransformer.votings_outcomes_normal_all_query(term_tag=term_tag).subquery()
        return (
            select(votings_outcomes.c.member_name)
            .where(votings_outcomes.c.group_name_short == DUMMY_GROUP_NAME_SHORT)
            .distinct()
        )

    @classmethod
    def voting_outcomes_normal_members_query(cls, term_tag: TermTag):
        voting_outcomes = AnalyticsTransformer.votings_outcomes_normal_all_query(term_tag=term_tag).subquery()
        voting_outcomes = (
            select(
                voting_outcomes.c.member_name,
                voting_outcomes.c.session_id,
                voting_outcomes.c.voting_id,
                voting_outcomes.c.group_name_short,
            )
            .order_by(
                voting_outcomes.c.member_name,
                voting_outcomes.c.session_id.cast(Integer),
                voting_outcomes.c.voting_id.cast(Integer)
            )
        ).subquery()

        member_voting_names = cls.member_voting_names(term_tag=term_tag).subquery()

        return (
            select(voting_outcomes)
            .outerjoin(member_voting_names, member_voting_names.c.member_name == voting_outcomes.c.member_name)
        )
