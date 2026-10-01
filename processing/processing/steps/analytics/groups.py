import pandas as pd

from processing.models.data.analytics.groups import Groups, GroupsMembersRotation, \
    GroupsVotingsOutcomesDisciplineRanking
from processing.models.tags import TermTag
from processing.steps.step import Step
from processing.transformers.analytics.groups import GroupsAnalyticsTransformer


class GroupsAnalyticsStep(Step):

    @classmethod
    def _groups(cls, term_tag: TermTag, session):
        query = GroupsAnalyticsTransformer.groups_query(term_tag=term_tag)
        return Groups.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def _groups_members_rotation(cls, term_tag: TermTag, session):
        query = GroupsAnalyticsTransformer.groups_members_diff_count_query(term_tag=term_tag)
        df = pd.read_sql_query(sql=query, con=session.connection())

        GROUP_NO_LONGER_EXISTS_VALUE = -999

        df = df[['datetime', 'group_name_short', 'diff']]
        df.datetime = pd.to_datetime(df.datetime)

        df = df.groupby(['group_name_short', pd.Grouper(key='datetime', axis=0, freq='D')]).last().reset_index(
            drop=False)
        df = df.pivot_table(index='datetime', columns='group_name_short', values='diff')
        df = df.reset_index(drop=False)
        df = df.sort_values('datetime')

        for column in df.columns:
            if column == 'datetime':
                continue

            df.loc[df[column].index > df[column].last_valid_index(), column] = GROUP_NO_LONGER_EXISTS_VALUE

        df_dates = pd.date_range(min(df.datetime), max(df.datetime), freq="D")
        df_dates = df_dates.to_frame().reset_index(drop=True)
        df_dates.columns = ['datetime']

        df = pd.merge(df_dates, df, on=['datetime'], how='left')
        df = df.ffill()

        df = df.melt(id_vars='datetime', var_name='group_name_short', value_name='group_rotation')
        df = df[df.group_rotation != GROUP_NO_LONGER_EXISTS_VALUE]

        return GroupsMembersRotation(tag=term_tag, df=df)

    @classmethod
    def _groups_votings_outcomes_discipline_ranking(cls, term_tag: TermTag, session):
        query = GroupsAnalyticsTransformer.groups_votings_outcomes_discipline_ranking_query(term_tag=term_tag)
        return GroupsVotingsOutcomesDisciplineRanking.from_query(tag=term_tag, query=query, session=session)

    @classmethod
    def run(cls, payload, *args, **kwargs):
        session = kwargs.get('session')

        term_tag = payload['term_tag']

        payload.update({
            "groups": cls._groups(term_tag=term_tag, session=session),
            "groups_members_rotation": cls._groups_members_rotation(term_tag=term_tag, session=session),
            "groups_votings_outcomes_discipline_ranking":
                cls._groups_votings_outcomes_discipline_ranking(term_tag=term_tag, session=session),
        })

        return payload
