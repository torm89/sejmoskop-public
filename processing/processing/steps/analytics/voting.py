from processing.models.data.analytics.voting import VotingRollCallAnalytics
from processing.models.tags import TermTag
from processing.steps.step import Step
from processing.transformers.analytics.voting import VotingRollCallAnalyticsTransformer


class VotingsAnalyticsStep(Step):

    @classmethod
    def _voting_roll_call(cls, term_tag: TermTag, session):
        query = VotingRollCallAnalyticsTransformer.voting_roll_call_query(term_tag=term_tag)
        return VotingRollCallAnalytics.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def run(cls, payload, *args, **kwargs):
        session = kwargs.get('session')

        term_tag = payload['term_tag']

        payload.update({
            "voting_roll_call": cls._voting_roll_call(term_tag, session=session),
        })

        return payload
