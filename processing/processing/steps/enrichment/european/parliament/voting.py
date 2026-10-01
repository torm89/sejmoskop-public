import datetime
import json
import logging
from typing import Dict

import pandas as pd
from cachetools import cached
from cachetools.keys import hashkey

from processing.models.data.preprocessing.member import MemberData
from processing.models.data.preprocessing.voting import VotingOutcomeData
from processing.models.tags import TermTag, VotingOutcomeCall, VotingOutcomeTag, VotingTag
from processing.steps.enrichment.enrichment import EnrichmentVotingOutcomesStep, \
    EnrichmentTermStep
from processing.transformers.enrichment.votings import VotingOutcomeNoVotedCallEnrichmentTransformerEuropeanParliament, \
    MemberVotingOutcomeDummyGroupNameShortEnrichmentTransformerEuropeanParliament, DUMMY_GROUP_NAME_SHORT, \
    VotingOutcomeNoMemberNameEnrichmentTransformerEuropeanParliament


class VotingOutcomeNoMemberNameEnrichmentStepEuropeanParliament(EnrichmentVotingOutcomesStep):

    @classmethod
    def _step_make_payload(cls, tag: VotingOutcomeTag, *args, **kwargs) -> Dict:
        repository = kwargs['repository']

        voting_tag = VotingTag(**tag.model_dump(by_alias=True))

        return {
            "voting_tag": voting_tag,
            "voting_outcome_data": repository.fetch_voting_outcome_data(tag=voting_tag)
        }

    @classmethod
    def _step_save_payload(cls, payload, *args, **kwargs):
        repository = kwargs['repository']

        repository.save(payload["voting_outcome_data"])

    @staticmethod
    @cached(cache={}, key=lambda term_tag, session: hashkey(term_tag))
    def _members(term_tag: TermTag, session):
        query = VotingOutcomeNoMemberNameEnrichmentTransformerEuropeanParliament.members_query(term_tag=term_tag)
        return MemberData.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _member_voting_name_from_member_table(cls, term_tag: TermTag, member_name: str, session):
        df = cls._members(term_tag, session=session).df
        df = df[df['last_name'].str.endswith(member_name)]

        if len(df) > 1:
            logging.warning(f"Multiple members found for {member_name}")

        return df['voting_name'].iloc[0] if not df.empty else member_name

    @classmethod
    def _step_run(cls, payload, *args, **kwargs) -> Dict:
        session = kwargs.get('session')

        tag, voting_outcome_data = payload['voting_tag'], payload['voting_outcome_data']
        term_tag = TermTag(chamberName=tag.chamber_name, termId=tag.term_id)

        for i, row in voting_outcome_data.df.iterrows():
            member_name = row['member_name']

            if not member_name.isdigit():
                member_name = cls._member_voting_name_from_member_table(
                    term_tag=term_tag, member_name=member_name, session=session)

                voting_outcome_data.df.loc[i, 'member_name'] = member_name

        payload.update({
            "voting_outcome_data": voting_outcome_data
        })

        return payload


class VotingOutcomeNoVotedCallEnrichmentStepEuropeanParliament(EnrichmentVotingOutcomesStep):

    @classmethod
    def _step_make_payload(cls, tag: VotingOutcomeTag, *args, **kwargs) -> Dict:
        repository = kwargs['repository']

        voting_tag = VotingTag(**tag.model_dump(by_alias=True))

        return {
            "voting_tag": voting_tag,
            "voting_data": repository.fetch_voting_data(tag=voting_tag),
            "voting_outcome_data": repository.fetch_voting_outcome_data(tag=voting_tag)
        }

    @classmethod
    def _step_save_payload(cls, payload, *args, **kwargs):
        repository = kwargs['repository']

        repository.save(payload["voting_outcome_data"])

    @staticmethod
    @cached(cache={}, key=lambda term_tag, session: hashkey(term_tag))
    def _members(term_tag: TermTag, session):
        query = VotingOutcomeNoVotedCallEnrichmentTransformerEuropeanParliament.members_query(term_tag=term_tag)
        return MemberData.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    @cached(cache={}, key=lambda cls, term_tag, date, session: hashkey(term_tag, date))
    def _member_ids_at_date(cls, term_tag: TermTag, date: datetime.date, session):
        members = cls._members(term_tag, session=session)

        member_ids = []
        for member in members.df.itertuples():
            former_details = json.loads(member.former_details)
            if former_details:
                mandate_start = former_details.get('mandate_start')
                mandate_end = former_details.get(
                    'mandate_end',
                    datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))

                mandate_start_date = datetime.datetime.strptime(mandate_start, "%Y-%m-%d").date()
                mandate_end_date = datetime.datetime.strptime(mandate_end, "%Y-%m-%d").date()

                if not (mandate_start_date <= date <= mandate_end_date):
                    continue

            member_ids.append(member.voting_name)

        return member_ids

    @classmethod
    def _member_ids_from_data(cls, data):
        return [row.member_name for row in data.df.itertuples()]

    @classmethod
    def _step_run(cls, payload, *args, **kwargs) -> Dict:
        session = kwargs.get('session')

        tag = payload['voting_tag']
        voting_data, voting_outcome_data = payload['voting_data'], payload['voting_outcome_data']

        voting_date = datetime.datetime.fromisoformat(voting_data.df.loc[0, 'datetime']).date()
        voting_type = voting_data.df.loc[0, 'voting_type']

        term_tag = TermTag(chamberName=tag.chamber_name, termId=tag.term_id)

        member_ids_at_date = cls._member_ids_at_date(term_tag, voting_date, session=session)
        member_ids = cls._member_ids_from_data(voting_outcome_data)

        # EP leaves member_id empty (the PersId rides in member_name), so emit ''
        # to match the now-7-column VotingOutcomeData shape.
        no_voted_data = [
            [tag.session_id, tag.voting_id, voting_type, member_name, DUMMY_GROUP_NAME_SHORT,
             VotingOutcomeCall.no_voted.value, '']
            for member_name in sorted(list(set(member_ids_at_date) - set(member_ids)))
        ]

        if no_voted_data:
            missing_df = pd.DataFrame(no_voted_data, columns=voting_outcome_data.columns)
            voting_outcome_data.df = pd.concat([voting_outcome_data.df, missing_df])

        payload.update({
            "voting_outcome_data": voting_outcome_data
        })

        return payload


class MemberVotingOutcomeGroupNameShortEnrichmentStepEuropeanParliament(EnrichmentTermStep):

    @classmethod
    def _step_make_payload(cls, tag: TermTag, *args, **kwargs) -> Dict:
        return {
            "term_tag": tag
        }

    @classmethod
    @cached(cache={}, key=lambda cls, term_tag, session: hashkey(term_tag))
    def _members_voting_outcomes_df(cls, term_tag: TermTag, session) -> pd.DataFrame:
        query = (
            MemberVotingOutcomeDummyGroupNameShortEnrichmentTransformerEuropeanParliament
            .voting_outcomes_normal_members_query(term_tag=term_tag)
        )
        return pd.read_sql_query(sql=query, con=session.connection())

    @classmethod
    def _step_run(cls, payload, *args, **kwargs) -> Dict:
        session = kwargs.get('session')

        term_tag = payload['term_tag']
        term_tag_dump = term_tag.model_dump(by_alias=True)

        df = cls._members_voting_outcomes_df(term_tag, session=session)
        df['tag'] = df.apply(
            lambda row: VotingOutcomeTag(**term_tag_dump, sessionId=row['session_id'], votingId=row['voting_id']),
            axis=1
        )
        df = df.pivot_table(index='tag', columns='member_name', values='group_name_short', aggfunc='first')
        df.replace(DUMMY_GROUP_NAME_SHORT, None, inplace=True)

        df_dummy_mask = df.isnull()

        df.ffill(inplace=True)
        df.bfill(inplace=True)

        df_T = df.where(df_dummy_mask, None).T
        df_T.dropna(inplace=True, how='all', axis=1)

        payload.update({"group_name_short_changes": df_T.to_dict()})

        return payload

    @classmethod
    def _step_save_payload(cls, step_payload, *args, **kwargs):
        repository = kwargs['repository']

        changes_by_tag = step_payload["group_name_short_changes"]

        total = len(changes_by_tag)
        log_every = max(1, total // 10)
        for idx, (voting_outcome_tag, changes) in enumerate(changes_by_tag.items()):
            if idx % log_every == 0 or idx == total - 1:
                logging.info(
                    f'-- enrichment (s) -- {(idx + 1) / total * 100:.2f}% -- {voting_outcome_tag}\t -- {cls}')

            voting_outcome_data = repository.fetch_voting_outcome_data(tag=voting_outcome_tag)

            df = pd.DataFrame(
                [(voting_outcome_tag.session_id, voting_outcome_tag.voting_id, member_name, group_name_short)
                 for member_name, group_name_short in changes.items() if group_name_short is not None],
                columns=['session_id', 'voting_id', 'member_name', 'group_name_short']
            )
            df.set_index(['session_id', 'voting_id', 'member_name'], inplace=True)

            voting_outcome_data.df.set_index(['session_id', 'voting_id', 'member_name'], inplace=True)
            voting_outcome_data.df.update(df)
            voting_outcome_data.df.reset_index(inplace=True, drop=False)
            voting_outcome_data.df = voting_outcome_data.df[VotingOutcomeData.columns2()]

            repository.save(voting_outcome_data)
