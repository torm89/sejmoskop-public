from typing import List, Dict, Type

from processing.models.data import Data, DataHot
from processing.models.tags import LegislationTag


class LegislationHotData(DataHot):
    pass


class LegislationData(Data[LegislationTag]):

    @classmethod
    def columns2(cls) -> List[str]:
        return ['legislation_number', 'title', 'document_type', 'passed', 'process_start_date', 'change_date',
                'closure_date']

    @property
    def columns(self) -> List[str]:
        return ['legislation_number', 'title', 'document_type', 'passed', 'process_start_date', 'change_date',
                'closure_date']

    @classmethod
    def columns_types2(cls) -> Dict[str, Type]:
        return {'legislation_number': str, 'title': str, 'document_type': str, 'passed': str,
                'process_start_date': str, 'change_date': str, 'closure_date': str}

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {'legislation_number': str, 'title': str, 'document_type': str, 'passed': str,
                'process_start_date': str, 'change_date': str, 'closure_date': str}


class LegislationStageData(Data[LegislationTag]):

    @classmethod
    def columns2(cls) -> List[str]:
        return ['legislation_number', 'stage_index', 'stage_name', 'stage_type', 'date', 'decision', 'print_numbers']

    @property
    def columns(self) -> List[str]:
        return ['legislation_number', 'stage_index', 'stage_name', 'stage_type', 'date', 'decision', 'print_numbers']

    @classmethod
    def columns_types2(cls) -> Dict[str, Type]:
        return {'legislation_number': str, 'stage_index': str, 'stage_name': str, 'stage_type': str, 'date': str,
                'decision': str, 'print_numbers': str}

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {'legislation_number': str, 'stage_index': str, 'stage_name': str, 'stage_type': str, 'date': str,
                'decision': str, 'print_numbers': str}


class LegislationVotingData(Data[LegislationTag]):

    @classmethod
    def columns2(cls) -> List[str]:
        return ['legislation_number', 'stage_index', 'session_id', 'voting_id']

    @property
    def columns(self) -> List[str]:
        return ['legislation_number', 'stage_index', 'session_id', 'voting_id']

    @classmethod
    def columns_types2(cls) -> Dict[str, Type]:
        return {'legislation_number': str, 'stage_index': str, 'session_id': str, 'voting_id': str}

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {'legislation_number': str, 'stage_index': str, 'session_id': str, 'voting_id': str}
