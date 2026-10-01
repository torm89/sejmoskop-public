from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.enrichment.european.parliament.voting import \
    VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament, \
    MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament, \
    VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament
from processing.steps.enrichment.sejm.statement import StatementMemberIdEnrichmentStepSejm
from processing.steps.enrichment.senat.statement import StatementMemberIdEnrichmentStepSenat
from processing.steps.step import Step


class EnrichmentPipelineSejm(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            StatementMemberIdEnrichmentStepSejm,
        ]


class EnrichmentPipelineSenat(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            StatementMemberIdEnrichmentStepSenat,
        ]


class EnrichmentPipelineEuropeanParliament(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament,
            VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament,
            MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament
        ]
