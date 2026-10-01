import base64
from typing import Dict

from processing.models.tags import GroupTag, GroupType

GROUP_NAME_GROUP_NAME_SHORT_MAPPING = {
    "Klub Parlamentarny Prawo i Sprawiedliwość": "PiS",
    "Klub Parlamentarny Koalicja Obywatelska - Platforma Obywatelska, Nowoczesna, Inicjatywa Polska, Zieloni": "KO",
    "Klub Senacki Trzecia Droga": "Trzecia Droga",
    "Koalicyjny Klub Parlamentarny Lewicy": "Lewica",
    "Koło Senackie Niezależni i Samorządni": "NiS",
}


class GroupProcessingTransformerSenat:

    @staticmethod
    def get_group_short_name_from_mapping(name: str):
        return GROUP_NAME_GROUP_NAME_SHORT_MAPPING.get(name, name)

    @staticmethod
    def add_group_name_short_field(tag: GroupTag, data: Dict):
        return {
            **data,
            "nameShort": GroupProcessingTransformerSenat.get_group_short_name_from_mapping(data['name'])
        }

    @staticmethod
    def fix_group_type_field(tag: GroupTag, data: Dict):
        mapping = {"KLUB": GroupType.KLUB, "KOLO": GroupType.KOLO, "": ""}

        if data['name'].startswith("Klub") or data['name'].startswith("Koalicyjny Klub"):
            data["groupType"] = "KLUB"
        elif data['name'].startswith("Koło") or data['name'].startswith("Parlamentarne Koło"):
            data["groupType"] = "KOLO"
        elif data['name'] == "Senatorowie niezrzeszeni":
            data["groupType"] = ""

        group_type = data["groupType"]
        return {
            **data,
            "groupType": mapping[group_type]
        }

    @staticmethod
    def extract_group_image(tag: GroupTag, data: Dict):
        return base64.b64decode(data.get("image", ''))
