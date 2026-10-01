from processing.models.tags import TermTag
from processing.steps.enrichment.statement import StatementMemberIdEnrichmentStep


class StatementMemberIdEnrichmentStepSenat(StatementMemberIdEnrichmentStep):

    @classmethod
    def additional_term_tag(cls, statement_tag: TermTag):
        return TermTag(chamberName='sejm', termId=str(int(statement_tag.term_id) - 1))
