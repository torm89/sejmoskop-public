from processing.models.data.analytics.members import Members, MembersVotingsOutcomesStats, \
    MembersVotingsOutcomesConsistencyChamber, MembersVotingsOutcomesConsistencyGroups, \
    MembersVotingsOutcomesNoVotedRanking, MembersVotingsOutcomesAbstainRanking, \
    MembersVotingsOutcomesRebelRanking
from processing.models.tags import TermTag
from processing.steps.step import Step
from processing.transformers.analytics.members import MembersAnalyticsTransformer


class MembersAnalyticsStep(Step):

    @classmethod
    def _members(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_groups_query(term_tag=term_tag)
        return Members.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _members_votings_outcomes_abstain_ranking(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_votings_outcomes_abstain_ranking_query(term_tag=term_tag)
        return MembersVotingsOutcomesAbstainRanking.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _members_votings_outcomes_no_voted_ranking(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_votings_outcomes_no_voted_ranking_query(term_tag=term_tag)
        return MembersVotingsOutcomesNoVotedRanking.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _members_votings_outcomes_rebel_ranking(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_votings_outcomes_rebel_ranking_query(term_tag=term_tag)
        return MembersVotingsOutcomesRebelRanking.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _members_voting_outcome_stats(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_voting_outcome_stats_query(term_tag=term_tag)
        return MembersVotingsOutcomesStats.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _members_votings_outcomes_consistency_chamber(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_votings_outcomes_consistency_chamber_query(term_tag=term_tag)
        return MembersVotingsOutcomesConsistencyChamber.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _members_votings_outcomes_consistency_groups(cls, term_tag: TermTag, session):
        query = MembersAnalyticsTransformer.members_votings_outcomes_consistency_groups_query(term_tag=term_tag)
        return MembersVotingsOutcomesConsistencyGroups.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def run(cls, payload, *args, **kwargs):
        session = kwargs.get('session')

        term_tag = payload['term_tag']

        payload.update({
            "members": cls._members(term_tag, session=session),
            "members_voting_outcome_abstain_ranking":
                cls._members_votings_outcomes_abstain_ranking(term_tag, session=session),
            "members_voting_outcome_no_voted_ranking":
                cls._members_votings_outcomes_no_voted_ranking(term_tag, session=session),
            "members_voting_outcome_rebel_ranking":
                cls._members_votings_outcomes_rebel_ranking(term_tag, session=session),
            "members_voting_outcome_stats": cls._members_voting_outcome_stats(term_tag, session=session),
            "members_voting_outcome_consistency_chamber":
                cls._members_votings_outcomes_consistency_chamber(term_tag, session=session),
            "members_voting_outcome_consistency_groups":
                cls._members_votings_outcomes_consistency_groups(term_tag, session=session),
        })

        return payload
