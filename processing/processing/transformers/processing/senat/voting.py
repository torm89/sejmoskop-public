from datetime import datetime
from typing import Dict, List

from processing.models.tags import VotingTag, VotingOutcomeTag, VotingType, VotingOutcomeCall
from processing.transformers.processing.senat.group import GroupProcessingTransformerSenat
from processing.utils.exceptions import NotHandleVotingTypeException


class VotingProcessingTransformerSenat:

    @staticmethod
    def add_datetime_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "datetime": datetime.strptime(f'{data["date"]} {data["time"]}', '%d-%m-%Y %H:%M:%S')
        }

    @staticmethod
    def add_description_03_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "description_03": ""
        }

    @staticmethod
    def fix_voting_type_field(tag: VotingTag, data: Dict):
        # mapping = {
        #     "ELECTRONIC": VotingType.NORMAL, "ON_LIST": VotingType.LIST, "TRADITIONAL": VotingType.TRADITIONAL
        # }
        #
        # voting_type = data["votingType"]
        return {
            **data,
            "votingType": VotingType.NORMAL
        }

    @staticmethod
    def _fix_voting_outcome_call_field(data: Dict):
        mapping = {
            "Za": VotingOutcomeCall.yea,
            "Przeciw": VotingOutcomeCall.nay,
            "Wstrzymał się": VotingOutcomeCall.abstain,
            "Nieobecny": VotingOutcomeCall.no_voted,
        }

        call = data["call"]
        return {
            **data,
            "call": mapping[call]
        }

    @staticmethod
    def _extract_outcome_normal_voting(tag: VotingTag, data: Dict) -> [List[Dict], VotingOutcomeTag]:
        voting_outcome_tag = VotingOutcomeTag(**tag.model_dump(by_alias=True))

        voting_outcome_data = []
        for outcome in data['outcome']:
            outcome = VotingProcessingTransformerSenat._fix_voting_outcome_call_field(outcome)

            voting_outcome_data.append({
                "chamberName": data['chamberName'],
                "termId": data['termId'],
                "sessionId": data['sessionId'],
                "votingId": data['votingId'],
                "votingType": data['votingType'],
                "groupNameShort":
                    GroupProcessingTransformerSenat.get_group_short_name_from_mapping(outcome['groupName']),
                "memberName": outcome['memberName'],
                "call": outcome["call"]
            })

        return voting_outcome_data, voting_outcome_tag

    @staticmethod
    def extract_outcome(tag: VotingTag, data: Dict) -> [List[Dict], VotingOutcomeTag]:
        return VotingProcessingTransformerSenat._extract_outcome_normal_voting(tag, data)

        # if data['votingType'] in ('ELECTRONIC', VotingType.NORMAL):
        #     return VotingProcessingTransformerSenat._extract_outcome_normal_voting(tag, data)
        # elif data['votingType'] in ('ON_LIST', VotingType.LIST):
        #     return None, None
        # elif data['votingType'] in ('TRADITIONAL', VotingType.TRADITIONAL):
        #     return None, None
        #
        # raise NotHandleVotingTypeException
