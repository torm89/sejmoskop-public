import base64
from typing import Dict

from processing.models.tags import GroupTag, GroupType


class GroupProcessingTransformerSejm:

    @staticmethod
    def fix_group_name_short_field(tag: GroupTag, data: Dict):
        return {
            **data,
            "nameShort": data["id"]
        }

    @staticmethod
    def fix_group_type_field(tag: GroupTag, data: Dict):
        mapping = {"KLUB": GroupType.KLUB, "KOLO": GroupType.KOLO, "": ""}

        if data['name'].startswith("Klub") or data['name'].startswith("Koalicyjny Klub"):
            data["groupType"] = "KLUB"
        elif data['name'].startswith("Koło"):
            data["groupType"] = "KOLO"
        elif data['name'] == "Posłowie niezrzeszeni":
            data["groupType"] = ""

        group_type = data["groupType"]
        return {
            **data,
            "groupType": mapping[group_type]
        }

    @staticmethod
    def extract_group_image(tag: GroupTag, data: Dict):
        return base64.b64decode(data.get("image", ''))
