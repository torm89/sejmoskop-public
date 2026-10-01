import logging
from typing import List, Union, Dict

import pandas as pd
from cachetools import cached
from cachetools.keys import hashkey

from processing.models.data.analytics.members import Members
from processing.models.data.preprocessing.statement import StatementData
from processing.models.tags import TermTag, MemberTag, StatementTag
from processing.steps.enrichment.enrichment import EnrichmentStatementsStep
from processing.transformers.enrichment.statements import StatementMemberIdEnrichmentTransformer


class MembersTableData(Members):

    @property
    def columns(self) -> List[str]:
        return [
            'member_id', 'first_name', 'second_name', 'last_name', 'member_type', 'birth_date', 'former_details'
        ]


class StatementMemberIdEnrichmentStep(EnrichmentStatementsStep):

    @staticmethod
    @cached(cache={}, key=lambda term_tag, session: hashkey(term_tag))
    def _members(term_tag: TermTag, session):
        query = StatementMemberIdEnrichmentTransformer.members_query(term_tag=term_tag)
        return MembersTableData.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _try_to_find_member_tag(cls, name: str, term_tag: TermTag, df_members):
        name_split = name.split(' ')

        rows_long = df_members[df_members['full_name_long'].str.endswith(' '.join(name_split[-3:]))]
        rows = df_members[df_members['full_name'].str.endswith(' '.join(name_split[-2:]))]

        member_id = None
        if rows_long.shape[0]:
            member_id = rows_long['member_id'].values[0]
        elif rows.shape[0]:
            member_id = rows['member_id'].values[0]
        elif name not in ['Głos z sali', 'Głosy z sali', 'Posłowie', 'Senatorowie']:
            logging.warning(f"Member not found: {name}")

        if member_id:
            member_tag = MemberTag(chamberName=term_tag.chamber_name, termId=term_tag.term_id, memberId=member_id)
            return member_tag.model_dump(by_alias=True)

        return None

    @staticmethod
    @cached(cache={}, key=lambda term_tag, session: hashkey(term_tag))
    def df_members_with_names(term_tag: TermTag, session) -> pd.DataFrame:
        members = StatementMemberIdEnrichmentStep._members(term_tag, session=session)

        df_members = members.df

        df_members['full_name'] = df_members['first_name'] + ' ' + df_members['last_name']
        df_members['full_name_long'] = \
            df_members['first_name'] + ' ' + df_members['second_name'] + ' ' + df_members['last_name']

        return df_members

    @classmethod
    def try_to_find_member_tag(cls, name: str, term_tag: TermTag, session) -> Union[MemberTag, None]:
        df_members = cls.df_members_with_names(term_tag, session=session)
        speaker_member_tag = cls._try_to_find_member_tag(name, term_tag, df_members)
        return speaker_member_tag or None

    @classmethod
    def main_term_tag(cls, statement_tag: TermTag):
        return TermTag(chamberName=statement_tag.chamber_name, termId=statement_tag.term_id)

    @classmethod
    def additional_term_tag(cls, statement_tag: TermTag):
        raise NotImplementedError

    @classmethod
    def _step_make_payload(cls, tag: StatementTag, *args, **kwargs) -> Dict:
        repository = kwargs['repository']

        return {
            "statement_tag": tag,
            "statement_data": repository.fetch_statement_data(tag=tag)
        }

    @classmethod
    def _step_run(cls, payload, *args, **kwargs) -> Dict:
        session = kwargs.get('session')

        statement_tag = payload['statement_tag']
        statement_data = payload['statement_data']

        main_term_tag = cls.main_term_tag(statement_tag=statement_tag)
        additional_term_tag = cls.additional_term_tag(statement_tag=statement_tag)

        speaker_name = statement_data.data['speaker']['name']
        speaker_member_tag = cls.try_to_find_member_tag(speaker_name, main_term_tag, session=session)
        if not speaker_member_tag:
            speaker_member_tag = cls.try_to_find_member_tag(speaker_name, additional_term_tag, session=session)
        if speaker_member_tag:
            statement_data.data['speaker']['member_tag'] = speaker_member_tag

        chairman_name = statement_data.data['chairman']['name']
        chairman_member_tag = cls.try_to_find_member_tag(chairman_name, main_term_tag, session=session)
        if not chairman_member_tag:
            chairman_member_tag = cls.try_to_find_member_tag(chairman_name, additional_term_tag, session=session)
        if chairman_member_tag:
            statement_data.data['chairman']['member_tag'] = chairman_member_tag

        for record in statement_data.data['timeline']:
            if 'speaking' in record:
                speaking_name = record['speaking']['name']
                speaking_member_tag = cls.try_to_find_member_tag(speaking_name, main_term_tag, session=session)
                if not speaking_member_tag:
                    speaking_member_tag = cls.try_to_find_member_tag(speaking_name, additional_term_tag,
                                                                     session=session)
                if speaking_member_tag:
                    record['speaking']['member_tag'] = speaking_member_tag

        payload.update({
            "statement_enriched_data": StatementData.from_dict(tag=statement_tag, data=statement_data.data)
        })

        return payload

    @classmethod
    def _step_save_payload(cls, payload, *args, **kwargs):
        repository = kwargs['repository']

        repository.save(payload["statement_enriched_data"])
