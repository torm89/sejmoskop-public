from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.senat.group import GroupProcessingStepSenat
from processing.steps.step import Step


class GroupProcessingPipelineSenat(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            GroupProcessingStepSenat,
        ]
