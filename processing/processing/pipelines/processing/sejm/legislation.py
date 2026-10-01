from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.sejm.legislation import LegislationProcessingStepSejm
from processing.steps.step import Step


class LegislationProcessingPipelineSejm(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            LegislationProcessingStepSejm,
        ]
