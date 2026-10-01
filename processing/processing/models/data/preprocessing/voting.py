from typing import List, Dict, Type

from processing.models.data import Data, DataHot
from processing.models.tags import VotingTag


class VotingHotData(DataHot):
    pass


class VotingData(Data[VotingTag]):

    # TODO: Clean this up
    @classmethod
    def columns2(cls) -> List[str]:
        return ['session_id', 'voting_id', 'voting_type', 'datetime', 'description_01', 'description_02',
                'description_03']

    @property
    def columns(self) -> List[str]:
        return ['session_id', 'voting_id', 'voting_type', 'datetime', 'description_01', 'description_02',
                'description_03']

    # TODO: Clean this up
    @classmethod
    def columns_types2(cls) -> Dict[str, Type]:
        return {'session_id': str, 'voting_id': str, 'voting_type': str, 'description_01': str, 'description_02': str}

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {'session_id': str, 'voting_id': str, 'voting_type': str, 'description_01': str, 'description_02': str}


class VotingOutcomeData(Data[VotingTag]):

    @classmethod
    def columns2(cls) -> List[str]:
        return ['session_id', 'voting_id', 'voting_type', "member_name", 'group_name_short', 'call', 'member_id']

    @property
    def columns(self) -> List[str]:
        return ['session_id', 'voting_id', 'voting_type', "member_name", 'group_name_short', 'call', 'member_id']

    @classmethod
    def columns_types2(cls) -> Dict[str, Type]:
        return {
            'session_id': str, 'voting_id': str, 'voting_type': str, 'group_name_short': str,
            'call': str, 'member_name': str, 'member_id': str
        }

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {
            'session_id': str, 'voting_id': str, 'voting_type': str, 'group_name_short': str,
            'call': str, 'member_name': str, 'member_id': str
        }

    def normalize_df(self):
        # Senat and EP outcomes don't produce member_id (only the Sejm captures
        # the MP id during voting processing); default it so the base column
        # filter doesn't fail. Check both names: from_dict feeds camelCase
        # (Sejm's 'memberId'), which the base rename turns into 'member_id'.
        if 'member_id' not in self.df.columns and 'memberId' not in self.df.columns:
            self.df['member_id'] = ''
        super().normalize_df()
