from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.processing.european.parliament.statement import StatementProcessingStepEuropeanParliament, \
    StatementInterpretationStepEuropeanParliament
from processing.steps.step import Step


class StatementProcessingPipelineEuropeanParliament(Pipeline):

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            StatementProcessingStepEuropeanParliament,
            StatementInterpretationStepEuropeanParliament
        ]
