from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.senat.voting import VotingProcessingStepSenat
from processing.steps.step import Step


class VotingProcessingPipelineSenat(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            VotingProcessingStepSenat,
        ]
