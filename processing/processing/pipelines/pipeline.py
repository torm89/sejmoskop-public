import logging
from abc import abstractmethod, ABC
from typing import List, Type

from processing.steps.step import Step


class Pipeline(ABC):

    @property
    @abstractmethod
    def steps(self) -> List[Type[Step]]:
        raise NotImplementedError

    def run(self, payload, *args, **kwargs):
        steps = self.steps
        pipeline_name = type(self).__name__
        total = len(steps)

        for index, step in enumerate(steps, start=1):
            step_name = step.__name__
            logging.info(f"[{pipeline_name}] step {index}/{total}: {step_name} - start")
            payload.update(step.run(payload, *args, **kwargs))
            logging.info(f"[{pipeline_name}] step {index}/{total}: {step_name} - done")

        return payload
