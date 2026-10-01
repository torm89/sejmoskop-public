from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.analytics.legislation import LegislationAnalyticsStep
from processing.steps.step import Step


class LegislationAnalyticsPipeline(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            LegislationAnalyticsStep,
        ]
