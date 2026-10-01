from typing import List, Dict, Type

from processing.models.data import Data
from processing.models.tags import TermTag


class StatementsSessionDayDetails(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['date', 'session_id', 'date_id']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class StatementsDetails(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return [
            'date', 'description_01', 'description_02', 'title_01', 'title_02', 'session_id', 'date_id', 'statement_id',
            'statement_id_new', 'video_url'
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}
