from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.sejm.group import GroupProcessingStepSejm
from processing.steps.step import Step


class GroupProcessingPipelineSejm(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            GroupProcessingStepSejm,
        ]
