from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.senat.statement import StatementProcessingStepSenat
from processing.steps.step import Step


class StatementProcessingPipelineSenat(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            StatementProcessingStepSenat,
        ]
