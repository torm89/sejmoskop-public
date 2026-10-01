from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.sejm.statement import StatementProcessingStepSejm
from processing.steps.step import Step


class StatementProcessingPipelineSejm(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            StatementProcessingStepSejm,
        ]
