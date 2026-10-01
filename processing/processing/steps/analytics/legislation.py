from processing.models.data.analytics.legislation import LegislationAnalytics, LegislationStagesAnalytics, \
    LegislationVotingsAnalytics
from processing.models.tags import TermTag
from processing.steps.step import Step
from processing.transformers.analytics.legislation import LegislationAnalyticsTransformer


class LegislationAnalyticsStep(Step):

    @classmethod
    def _legislation(cls, term_tag: TermTag, session):
        query = LegislationAnalyticsTransformer.legislation_query(term_tag=term_tag)
        return LegislationAnalytics.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _legislation_stages(cls, term_tag: TermTag, session):
        query = LegislationAnalyticsTransformer.legislation_stages_query(term_tag=term_tag)
        return LegislationStagesAnalytics.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _legislation_votings(cls, term_tag: TermTag, session):
        query = LegislationAnalyticsTransformer.legislation_votings_query(term_tag=term_tag)
        return LegislationVotingsAnalytics.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def run(cls, payload, *args, **kwargs):
        session = kwargs.get('session')

        term_tag = payload['term_tag']

        payload.update({
            "legislation": cls._legislation(term_tag, session=session),
            "legislation_stages": cls._legislation_stages(term_tag, session=session),
            "legislation_votings": cls._legislation_votings(term_tag, session=session),
        })

        return payload
