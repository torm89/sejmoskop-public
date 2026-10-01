from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.sejm.voting import VotingProcessingStepSejm
from processing.steps.step import Step


class VotingProcessingPipelineSejm(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            VotingProcessingStepSejm,
        ]
