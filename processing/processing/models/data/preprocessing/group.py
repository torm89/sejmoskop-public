from dataclasses import dataclass
from typing import Dict, Type, List

from processing.models.data import Data, DataHot
from processing.models.tags import GroupTag


class GroupHotData(DataHot):
    pass


class GroupData(Data[GroupTag]):
    @property
    def columns(self) -> List[str]:
        return ['name', 'name_short', 'group_type']

    @property
    def columns_types(self) -> Dict[str, Type]:
        return {'name': str, 'name_short': str, 'group_type': str, }


@dataclass
class GroupImageData:
    tag: GroupTag
    data: bytes

    @classmethod
    def from_dict(cls, tag: GroupTag, data):
        return cls(tag=tag, data=data)

    def to_file_bytes(self) -> bytes:
        return self.data
