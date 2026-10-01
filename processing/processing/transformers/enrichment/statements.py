from processing.models.tags import TermTag
from processing.transformers.analytics import AnalyticsTransformer


class StatementMemberIdEnrichmentTransformer:

    @staticmethod
    def members_query(term_tag: TermTag):
        return AnalyticsTransformer.members_query(term_tag=term_tag)
