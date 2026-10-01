from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.analytics.groups import GroupsAnalyticsStep
from processing.steps.analytics.members import MembersAnalyticsStep
from processing.steps.step import Step


class AnalyticsPipeline(Pipeline):
    @property
    def steps(self) -> List[Type[Step]]:
        return [
            GroupsAnalyticsStep,
            MembersAnalyticsStep,
        ]
