from typing import List, Dict, Type

from processing.models.data import Data
from processing.models.tags import TermTag


class VotingRollCallAnalytics(Data[TermTag]):
    """Per-MP roll-call for every normal voting of a term, exported one file
    per voting so the web can read it instead of the live Sejm API."""

    @property
    def columns(self) -> List[str]:
        return [
            'session_id', 'voting_id',
            'member_id', 'first_name', 'second_name', 'last_name', 'group_name_short',
            'vote', 'date',
            'description_01', 'description_02',
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}
