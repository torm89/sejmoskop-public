from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.senat.member import MemberProcessingStepSenat
from processing.steps.step import Step


class MemberProcessingPipelineSenat(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            MemberProcessingStepSenat,
        ]
