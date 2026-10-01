from datetime import datetime
from typing import Dict, List

from processing.models.tags import VotingTag, VotingOutcomeTag, VotingType, VotingOutcomeCall
from processing.utils.exceptions import NotHandleVotingTypeException


class VotingProcessingTransformerSejm:

    @staticmethod
    def add_datetime_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "datetime": datetime.strptime(f'{data["date"]}', '%Y-%m-%dT%H:%M:%S')
        }

    @staticmethod
    def add_description_03_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "description_03": data.get("description", '')
        }

    @staticmethod
    def fix_voting_type_field(tag: VotingTag, data: Dict):
        mapping = {
            "ELECTRONIC": VotingType.NORMAL, "ON_LIST": VotingType.LIST, "TRADITIONAL": VotingType.TRADITIONAL
        }
        voting_type = mapping[data["votingType"]]

        if data.get("description02") == "Głosowanie kworum":
            voting_type = VotingType.QUORUM

        return {
            **data,
            "votingType": voting_type
        }

    @staticmethod
    def _fix_voting_outcome_call_field(data: Dict):
        mapping = {
            "YES": VotingOutcomeCall.yea,
            "NO": VotingOutcomeCall.nay,
            "ABSTAIN": VotingOutcomeCall.abstain,
            "ABSENT": VotingOutcomeCall.no_voted,
            "NO_VOTE": VotingOutcomeCall.no_voted,
        }

        call = data["vote"]
        return {
            **data,
            "call": mapping[call]
        }

    @staticmethod
    def _extract_outcome_normal_voting(tag: VotingTag, data: Dict) -> [List[Dict], VotingOutcomeTag]:
        voting_outcome_tag = VotingOutcomeTag(**tag.model_dump(by_alias=True))

        voting_outcome_data = []
        for outcome in data['outcome']:
            outcome = VotingProcessingTransformerSejm._fix_voting_outcome_call_field(outcome)

            voting_outcome_data.append({
                "chamberName": data['chamberName'],
                "termId": data['termId'],
                "sessionId": data['sessionId'],
                "votingId": data['votingId'],
                "votingType": data['votingType'],
                "groupNameShort": outcome['club'],
                "memberName":
                    f'{outcome["lastName"]} {outcome["firstName"]} {outcome.get("secondName", "")}'.strip(),
                "memberId": outcome['MP'],
                "call": outcome["call"]
            })

        return voting_outcome_data, voting_outcome_tag

    @staticmethod
    def extract_outcome(tag: VotingTag, data: Dict) -> [List[Dict], VotingOutcomeTag]:
        if data['votingType'] in ('ELECTRONIC', VotingType.NORMAL):
            return VotingProcessingTransformerSejm._extract_outcome_normal_voting(tag, data)
        elif data['votingType'] in ('ON_LIST', VotingType.LIST):
            return None, None
        elif data['votingType'] in ('TRADITIONAL', VotingType.TRADITIONAL):
            return None, None
        elif data['votingType'] in ('QUORUM', VotingType.QUORUM):
            return None, None

        raise NotHandleVotingTypeException
