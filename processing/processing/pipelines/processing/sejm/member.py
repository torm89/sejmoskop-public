from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.sejm.member import MemberProcessingStepSejm
from processing.steps.step import Step


class MemberProcessingPipelineSejm(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            MemberProcessingStepSejm,
        ]
