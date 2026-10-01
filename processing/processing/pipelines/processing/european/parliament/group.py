from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.european.parliament.group import GroupProcessingStepEuropeanParliament
from processing.steps.step import Step


class GroupProcessingPipelineEuropeanParliament(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            GroupProcessingStepEuropeanParliament,
        ]
