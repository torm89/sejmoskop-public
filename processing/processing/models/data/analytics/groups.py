from typing import List, Dict, Type

from processing.models.data import Data
from processing.models.tags import TermTag


class Groups(Data[TermTag]):

    @property
    def columns(self) -> List[str]:
        return ['name', 'name_short', 'group_type']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {'name': str, 'name_short': str, 'group_type': str, }


class GroupsMembersRotation(Data[TermTag]):

    @property
    def columns(self) -> List[str]:
        return ['datetime', 'group_name_short', 'group_rotation']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class GroupsVotingsOutcomesDisciplineRanking(Data[TermTag]):

    @property
    def columns(self) -> List[str]:
        return ['group_name_short', 'rank', 'percentage']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}
