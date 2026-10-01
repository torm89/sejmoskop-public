from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.european.parliament.member import MemberProcessingStepEuropeanParliament
from processing.steps.step import Step


class MemberProcessingPipelineEuropeanParliament(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            MemberProcessingStepEuropeanParliament,
        ]
