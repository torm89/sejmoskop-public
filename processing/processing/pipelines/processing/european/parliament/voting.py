from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.european.parliament.voting import VotingProcessingStepEuropeanParliament
from processing.steps.step import Step


class VotingProcessingPipelineEuropeanParliament(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            VotingProcessingStepEuropeanParliament,
        ]
