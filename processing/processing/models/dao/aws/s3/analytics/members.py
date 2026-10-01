from typing import Any, List, Union

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from processing.models.dao.aws.s3.analytics import TagAnalyticsDaoAwsS3, TagTagsAnalyticsDaoAwsS3
from processing.models.data.analytics.members import Members, MembersVotingsOutcomesStats, \
    MembersVotingsOutcomesConsistencyChamber, MembersVotingsOutcomesConsistencyGroups, \
    MembersVotingsOutcomesAbstainRanking, MembersVotingsOutcomesNoVotedRanking, \
    MembersVotingsOutcomesRebelRanking
from processing.models.tags import TermTag


def df_filter(data: Any) -> pd.DataFrame:
    if data.tag.chamber_name == 'european-parliament' and 'country' in data.df.columns:
        return data.df[data.df['country'] == 'Polska']
    return data.df


def group_by(data: Any, by: Union[List[str], str]) -> DataFrameGroupBy:
    return df_filter(data).groupby(by)


class MembersDaoAwsS3(TagTagsAnalyticsDaoAwsS3[TermTag, Members]):

    @property
    def by_column_name(self) -> str:
        return 'member_id'

    def data_df(self, data: Members) -> pd.DataFrame:
        return df_filter(data)

    def group_by(self, data: Members) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/members.json"

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by}/member.json"


class MembersVotingOutcomeAbstainRankingDaoAwsS3(
    TagTagsAnalyticsDaoAwsS3[TermTag, MembersVotingsOutcomesAbstainRanking]
):

    @property
    def by_column_name(self) -> str:
        return 'member_id'

    def data_df(self, data: MembersVotingsOutcomesAbstainRanking) -> pd.DataFrame:
        return df_filter(data)

    def group_by(self, data: MembersVotingsOutcomesAbstainRanking) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/members_votings_outcomes_abstain_ranking.json"

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by}/member_votings_outcomes_abstain_ranking.json"


class MembersVotingOutcomeNoVotedRankingDaoAwsS3(
    TagTagsAnalyticsDaoAwsS3[TermTag, MembersVotingsOutcomesNoVotedRanking]
):

    @property
    def by_column_name(self) -> str:
        return 'member_id'

    def data_df(self, data: MembersVotingsOutcomesNoVotedRanking) -> pd.DataFrame:
        return df_filter(data)

    def group_by(self, data: MembersVotingsOutcomesNoVotedRanking) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/members_votings_outcomes_no_voted_ranking.json"

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by}/member_votings_outcomes_no_voted_ranking.json"


class MembersVotingOutcomeRebelRankingDaoAwsS3(
    TagTagsAnalyticsDaoAwsS3[TermTag, MembersVotingsOutcomesRebelRanking]
):

    @property
    def by_column_name(self) -> str:
        return 'member_id'

    def data_df(self, data: MembersVotingsOutcomesRebelRanking) -> pd.DataFrame:
        return df_filter(data)

    def group_by(self, data: MembersVotingsOutcomesRebelRanking) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/members_votings_outcomes_rebel_ranking.json"

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by}/member_votings_outcomes_rebel_ranking.json"


class MembersVotingsOutcomesStatsDaoAwsS3(TagAnalyticsDaoAwsS3[TermTag, MembersVotingsOutcomesStats]):

    @property
    def by_column_name(self) -> List[str]:
        return ['member_id']

    def group_by(self, data: MembersVotingsOutcomesStats) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by[0]}/member_votings_outcomes_stats.json"


class MembersVotingsOutcomesConsistencyChamberDaoAwsS3(
    TagAnalyticsDaoAwsS3[TermTag, MembersVotingsOutcomesConsistencyChamber]
):

    @property
    def by_column_name(self) -> List[str]:
        return ['member_id']

    def group_by(self, data: MembersVotingsOutcomesConsistencyChamber) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by[0]}/member_votings_outcomes_consistency_chamber.json"


class MembersVotingsOutcomesConsistencyGroupsDaoAwsS3(
    TagAnalyticsDaoAwsS3[TermTag, MembersVotingsOutcomesConsistencyGroups]
):

    @property
    def by_column_name(self) -> List[str]:
        return ['member_id']

    def group_by(self, data: MembersVotingsOutcomesConsistencyGroups) -> DataFrameGroupBy:
        return group_by(data, self.by_column_name)

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/members/{tag.chamber_name}/{tag.term_id}/{by[0]}/member_votings_outcomes_consistency_groups.json"
