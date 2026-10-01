from typing import Dict

from processing.models.tags import GroupTag


class GroupProcessingTransformerEuropeanParliament:

    @staticmethod
    def add_group_name_short_field(tag: GroupTag, data: Dict):
        return {
            **data,
            "nameShort": data["id"]
        }

    @staticmethod
    def add_group_type_field(tag: GroupTag, data: Dict):
        return {
            **data,
            "groupType": ""
        }

