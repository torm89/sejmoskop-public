from dataclasses import dataclass
from typing import List, Dict, Type

from processing.models.data import Data, DataHot
from processing.models.tags import MemberTag


class MemberHotData(DataHot):
    pass


# TODO: Change to TermTag
class MemberData(Data[MemberTag]):

    @property
    def columns(self) -> List[str]:
        return [
            'member_id', 'first_name', 'second_name', 'last_name', 'member_type', 'voting_name', 'birth_date',
            'former_details', 'country'
        ]

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {
            'member_id': str, 'first_name': str, 'second_name': str, 'last_name': str, 'member_type': str,
            'voting_name': str, 'former_details': str, 'country': str
        }


@dataclass
class MemberImageData:
    tag: MemberTag
    data: bytes

    @classmethod
    def from_dict(cls, tag: MemberTag, data):
        return cls(tag=tag, data=data)

    def to_file_bytes(self) -> bytes:
        return self.data
