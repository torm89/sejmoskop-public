from datetime import datetime
from typing import Dict, List

from cachetools import cached
from cachetools.keys import hashkey

from processing.models.tags import VotingTag, VotingOutcomeTag, VotingType, VotingOutcomeCall


class GroupCallOutcomesNotFoundException(Exception):
    pass


class VotingProcessingTransformerEuropeanParliament:
    CALL_MAPPING = {
        'Result.For': VotingOutcomeCall.yea,
        'Result.Against': VotingOutcomeCall.nay,
        'Result.Abstention': VotingOutcomeCall.abstain
    }

    @staticmethod
    def add_datetime_field(tag: VotingTag, data: Dict):
        dt = datetime.strptime(f'{data["date"]}T00:00:00', '%Y-%m-%dT%H:%M:%S')
        return {
            **data,
            "datetime": dt.isoformat()
        }

    @staticmethod
    def add_description_01_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "description_01": ""
        }

    @staticmethod
    def add_description_02_field(tag: VotingTag, data: Dict):
        description = data.get('data', {}).get("RollCallVote.Description.Text", {})
        if isinstance(description, dict):
            description = description.get("#text", '')

        return {
            **data,
            "description_02": description
        }

    @staticmethod
    def add_description_03_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "description_03": ""
        }

    @staticmethod
    def fix_voting_type_field(tag: VotingTag, data: Dict):
        return {
            **data,
            "votingType": VotingType.NORMAL
        }

    @staticmethod
    @cached(cache={}, key=lambda tag, data: hashkey(tag))
    def attendance_register_member_pers_ids_from_mapping(tag: VotingTag, data: Dict):
        attendance_register = data.get('attendanceRegister', {}).get('PV.AttendanceRegister', {})

        present = attendance_register.get('Attendance.Participant.Name', [])
        excused = attendance_register.get('Attendance.Excused.Name', [])

        if isinstance(present, dict):
            present = [present]
        if isinstance(excused, dict):
            excused = [excused]

        return {
            record['#text']: record['@_MEP.Identifier'] for record in present + excused
        }

    @classmethod
    def extract_member_name_from_attendance_register(cls, record: Dict, tag: VotingTag, data: Dict) -> str:
        name = record.get('#text', '')
        for pers_name, pers_id in cls.attendance_register_member_pers_ids_from_mapping(tag, data).items():
            if name in pers_name:
                return pers_id

        return name

    @classmethod
    def extract_member_name(cls, record: Dict, tag: VotingTag, data: Dict) -> str:
        return record.get('@_PersId', cls.extract_member_name_from_attendance_register(record, tag, data))

    @classmethod
    def extract_voting_outcomes(cls, tag: VotingTag, data: Dict) -> [List[Dict], VotingOutcomeTag]:
        voting_outcome_tag = VotingOutcomeTag(**tag.model_dump(by_alias=True))

        voting_outcome_data = []
        for call_key in ['Result.For', 'Result.Against', 'Result.Abstention']:
            if call_key in data['data'] and 'Result.PoliticalGroup.List' in data['data'][call_key]:
                groups_call_outcomes = data['data'][call_key]['Result.PoliticalGroup.List']

                if isinstance(groups_call_outcomes, dict):
                    groups_call_outcomes = [groups_call_outcomes]

                for group_call_outcomes in groups_call_outcomes:
                    group_name_short = group_call_outcomes['@_Identifier']

                    group_call_members_outcomes = (
                            group_call_outcomes.get('PoliticalGroup.Member.Name', None) or
                            group_call_outcomes.get('Member.Name', None))
                    if group_call_members_outcomes is None:
                        raise GroupCallOutcomesNotFoundException

                    if isinstance(group_call_members_outcomes, dict):
                        group_call_members_outcomes = [group_call_members_outcomes]

                    for member_outcome in group_call_members_outcomes:
                        voting_outcome_data.append({
                            **tag.model_dump(by_alias=True),
                            "groupNameShort": group_name_short,
                            "memberName": cls.extract_member_name(member_outcome, tag, data),
                            "call": cls.CALL_MAPPING[call_key].value,
                            "votingType": VotingType.NORMAL.value
                        })

        for call_key in ['Result.For', 'Result.Against', 'Result.Abstention']:
            intention_call_key = f'Intentions.{call_key}'

            if 'Intentions' in data['data'] and intention_call_key in data['data']['Intentions']:
                intentions_call_outcomes = data['data']['Intentions'][intention_call_key]["Member.Name"]

                if isinstance(intentions_call_outcomes, dict):
                    intentions_call_outcomes = [intentions_call_outcomes]

                for intention in intentions_call_outcomes:
                    member_name = cls.extract_member_name(intention, tag, data)

                    for idx, outcome in enumerate(voting_outcome_data):
                        if outcome["memberName"] == member_name:
                            voting_outcome_data[idx]["call"] = cls.CALL_MAPPING[call_key].value
                            member_name = None
                            break

                    if member_name:
                        voting_outcome_data.append({
                            **tag.model_dump(by_alias=True),
                            "groupNameShort": "",
                            "memberName": member_name,
                            "call": cls.CALL_MAPPING[call_key].value,
                            "votingType": VotingType.NORMAL.value
                        })

        return voting_outcome_data, voting_outcome_tag
