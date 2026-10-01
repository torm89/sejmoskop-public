from typing import List, Dict, Type

from processing.models.data import Data
from processing.models.tags import TermTag


class LegislationAnalytics(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return [
            'legislation_number', 'title', 'document_type', 'passed', 'process_start_date', 'change_date',
            'closure_date'
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class LegislationStagesAnalytics(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['legislation_number', 'stage_index', 'stage_name', 'stage_type', 'date', 'decision', 'print_numbers']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class LegislationVotingsAnalytics(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return [
            'legislation_number', 'stage_index', 'session_id', 'voting_id', 'datetime', 'description_01',
            'description_02'
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}
