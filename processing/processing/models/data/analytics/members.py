from typing import List, Dict, Type

from processing.models.data import Data
from processing.models.tags import TermTag


class Members(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return [
            'member_id', 'first_name', 'second_name', 'last_name', 'member_type', 'birth_date', 'group_name_short',
            'former_details', 'country'
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class MembersVotingsOutcomesAbstainRanking(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['member_id', 'member_type', 'first_name', 'last_name', 'group_name_short', 'rank', 'percentage']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class MembersVotingsOutcomesNoVotedRanking(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['member_id', 'member_type', 'first_name', 'last_name', 'group_name_short', 'rank', 'percentage']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class MembersVotingsOutcomesRebelRanking(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['member_id', 'member_type', 'first_name', 'last_name', 'group_name_short', 'rank', 'percentage']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class MembersVotingsOutcomesStats(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['member_id', 'country', 'call', 'count']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class MembersVotingsOutcomesConsistencyChamber(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return [
            'member_id', 'country', 'session_id', 'voting_id', 'consistency_average_b20', 'consistency_average_b50',
            'consistency_average_b100'
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}


class MembersVotingsOutcomesConsistencyGroups(Data[TermTag]):
    @property
    def columns(self) -> List[str]:
        return ['member_id', 'country', 'group_reference_name_short', 'consistency_average']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {}
