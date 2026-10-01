from typing import List, Type

from processing.pipelines.pipeline import Pipeline
from processing.steps.analytics.voting import VotingsAnalyticsStep
from processing.steps.step import Step


class VotingsPipeline(Pipeline):
    """Per-voting roll-call export, isolated from the main analytics so a failure
    here cannot block the members/groups/rankings exports."""

    @property
    def steps(self) -> List[Type[Step]]:
        return [
            VotingsAnalyticsStep,
        ]
