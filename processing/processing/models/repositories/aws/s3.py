from datetime import datetime
from typing import List

from processing.models.dao import D
from processing.models.dao.aws.s3.analytics.groups import GroupsDaoAwsS3, GroupsMembersRotationDaoAwsS3, \
    GroupsVotingsOutcomesDisciplineRankingDaoAwsS3
from processing.models.dao.aws.s3.analytics.members import MembersDaoAwsS3, MembersVotingsOutcomesStatsDaoAwsS3, \
    MembersVotingsOutcomesConsistencyChamberDaoAwsS3, MembersVotingsOutcomesConsistencyGroupsDaoAwsS3, \
    MembersVotingOutcomeAbstainRankingDaoAwsS3, MembersVotingOutcomeNoVotedRankingDaoAwsS3, \
    MembersVotingOutcomeRebelRankingDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.group import GroupDaoAwsS3, GroupImageDaoAwsS3, GroupHotDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.member import MemberHotDaoAwsS3, MemberDaoAwsS3, MemberImageDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.statement import StatementHotDaoAwsS3, StatementDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.voting import VotingHotDaoAwsS3, VotingDaoAwsS3, VotingOutcomeDaoAwsS3
from processing.models.dao.aws.s3.preprocessing.legislation import LegislationHotDaoAwsS3, LegislationDaoAwsS3, \
    LegislationStageDaoAwsS3, LegislationVotingDaoAwsS3
from processing.models.dao.aws.s3.analytics.legislation import LegislationDaoAwsS3 as LegislationAnalyticsDaoAwsS3, \
    LegislationStagesDaoAwsS3, LegislationVotingsDaoAwsS3
from processing.models.dao.aws.s3.analytics.voting import VotingRollCallDaoAwsS3
from processing.models.data.analytics.groups import Groups, GroupsMembersRotation, \
    GroupsVotingsOutcomesDisciplineRanking
from processing.models.data.analytics.members import Members, MembersVotingsOutcomesStats, \
    MembersVotingsOutcomesConsistencyChamber, MembersVotingsOutcomesConsistencyGroups, \
    MembersVotingsOutcomesAbstainRanking, MembersVotingsOutcomesNoVotedRanking, \
    MembersVotingsOutcomesRebelRanking
from processing.models.data.preprocessing.group import GroupData, GroupImageData
from processing.models.data.preprocessing.member import MemberData, MemberImageData
from processing.models.data.preprocessing.statement import StatementData
from processing.models.data.preprocessing.voting import VotingData, VotingOutcomeData
from processing.models.data.preprocessing.legislation import LegislationData, LegislationStageData, \
    LegislationVotingData
from processing.models.data.analytics.legislation import LegislationAnalytics, LegislationStagesAnalytics, \
    LegislationVotingsAnalytics
from processing.models.data.analytics.voting import VotingRollCallAnalytics
from processing.models.tags import MemberTag, VotingTag, TermTag, GroupTag, StatementTag, VotingOutcomeTag, \
    LegislationTag
from processing.utils.exceptions import S3RepositoryException


class S3Repository:
    def __init__(self):
        self.member_hot_dao_aws_s3 = MemberHotDaoAwsS3()
        self.voting_hot_dao_aws_s3 = VotingHotDaoAwsS3()
        self.group_hot_dao_aws_s3 = GroupHotDaoAwsS3()
        self.statement_hot_dao_aws_s3 = StatementHotDaoAwsS3()
        self.legislation_hot_dao_aws_s3 = LegislationHotDaoAwsS3()

        self.member_dao_aws_s3 = MemberDaoAwsS3()
        self.member_image_dao_aws_s3 = MemberImageDaoAwsS3()
        self.voting_dao_aws_s3 = VotingDaoAwsS3()
        self.voting_outcome_dao_aws_s3 = VotingOutcomeDaoAwsS3()
        self.group_dao_aws_s3 = GroupDaoAwsS3()
        self.group_image_dao_aws_s3 = GroupImageDaoAwsS3()

        self.statement_dao_aws_s3 = StatementDaoAwsS3()

        self.legislation_dao_aws_s3 = LegislationDaoAwsS3()
        self.legislation_stage_dao_aws_s3 = LegislationStageDaoAwsS3()
        self.legislation_voting_dao_aws_s3 = LegislationVotingDaoAwsS3()

        self.groups_dao_aws_s3 = GroupsDaoAwsS3()
        self.groups_members_rotation_dao_aws_s3 = GroupsMembersRotationDaoAwsS3()
        self.groups_votings_outcomes_discipline_ranking_dao_aws_s3 = GroupsVotingsOutcomesDisciplineRankingDaoAwsS3()

        self.members_dao_aws_s3 = MembersDaoAwsS3()
        self.members_voting_outcome_abstain_ranking_dao_aws_s3 = MembersVotingOutcomeAbstainRankingDaoAwsS3()
        self.members_voting_outcome_no_voted_ranking_dao_aws_s3 = MembersVotingOutcomeNoVotedRankingDaoAwsS3()
        self.members_voting_outcome_rebel_ranking_dao_aws_s3 = MembersVotingOutcomeRebelRankingDaoAwsS3()
        self.members_votings_outcomes_stats_dao_aws_s3 = MembersVotingsOutcomesStatsDaoAwsS3()
        self.members_votings_outcomes_consistency_chamber_dao_aws_s3 = MembersVotingsOutcomesConsistencyChamberDaoAwsS3()
        self.members_votings_outcomes_consistency_groups_dao_aws_s3 = MembersVotingsOutcomesConsistencyGroupsDaoAwsS3()

        self.legislation_analytics_dao_aws_s3 = LegislationAnalyticsDaoAwsS3()
        self.legislation_stages_analytics_dao_aws_s3 = LegislationStagesDaoAwsS3()
        self.legislation_votings_analytics_dao_aws_s3 = LegislationVotingsDaoAwsS3()

        self.voting_roll_call_analytics_dao_aws_s3 = VotingRollCallDaoAwsS3()

    def list_member_hot_data(self, term_tag: TermTag):
        return self.member_hot_dao_aws_s3.list(term_tag=term_tag)

    def fetch_member_hot_data(self, tag: MemberTag):
        return self.member_hot_dao_aws_s3.get(tag=tag)

    def list_group_hot_data(self, term_tag: TermTag):
        return self.group_hot_dao_aws_s3.list(term_tag=term_tag)

    def fetch_group_hot_data(self, tag: GroupTag):
        return self.group_hot_dao_aws_s3.get(tag=tag)

    def list_voting_hot_data(self, term_tag: TermTag):
        return self.voting_hot_dao_aws_s3.list(term_tag=term_tag)

    def fetch_voting_hot_data(self, tag: VotingTag):
        return self.voting_hot_dao_aws_s3.get(tag=tag)

    def list_statement_hot_data(self, term_tag: TermTag):
        return self.statement_hot_dao_aws_s3.list(term_tag=term_tag)

    def fetch_statement_hot_data(self, tag: StatementTag):
        return self.statement_hot_dao_aws_s3.get(tag=tag)

    def list_legislation_hot_data(self, term_tag: TermTag):
        return self.legislation_hot_dao_aws_s3.list(term_tag=term_tag)

    def fetch_legislation_hot_data(self, tag: LegislationTag):
        return self.legislation_hot_dao_aws_s3.get(tag=tag)

    def list_member_data(self, term_tag: TermTag):
        return self.member_dao_aws_s3.list(term_tag=term_tag)

    def list_member_data_younger_than(self, term_tag: TermTag, date: datetime):
        return self.member_dao_aws_s3.list_younger_than(term_tag=term_tag, date=date)

    def fetch_member_data(self, tag: MemberTag):
        return self.member_dao_aws_s3.get(tag=tag)

    def fetch_member_image(self, tag: MemberTag) -> MemberImageData:
        return self.member_image_dao_aws_s3.get(tag=tag)

    def list_voting_data(self, term_tag: TermTag):
        return self.voting_dao_aws_s3.list(term_tag=term_tag)

    def list_voting_data_younger_than(self, term_tag: TermTag, date: datetime):
        return self.voting_dao_aws_s3.list_younger_than(term_tag=term_tag, date=date)

    def fetch_voting_data(self, tag: VotingTag):
        return self.voting_dao_aws_s3.get(tag=tag)

    def fetch_voting_outcome_data(self, tag: VotingOutcomeTag):
        return self.voting_outcome_dao_aws_s3.get(tag=tag)

    def list_voting_outcome_data(self, term_tag: TermTag):
        return self.voting_outcome_dao_aws_s3.list(term_tag=term_tag)

    def list_voting_outcome_data_younger_than(self, term_tag: TermTag, date: datetime):
        return self.voting_outcome_dao_aws_s3.list_younger_than(term_tag=term_tag, date=date)

    def list_group_data(self, term_tag: TermTag):
        return self.group_dao_aws_s3.list(term_tag=term_tag)

    def list_group_data_younger_than(self, term_tag: TermTag, date: datetime):
        return self.group_dao_aws_s3.list_younger_than(term_tag=term_tag, date=date)

    def fetch_group_data(self, tag: GroupTag):
        return self.group_dao_aws_s3.get(tag=tag)

    def list_statement_data(self, term_tag: TermTag):
        return self.statement_dao_aws_s3.list(term_tag=term_tag)

    def list_statement_data_younger_than(self, term_tag: TermTag, date: datetime):
        return self.statement_dao_aws_s3.list_younger_than(term_tag=term_tag, date=date)

    def fetch_statement_data(self, tag: StatementTag):
        return self.statement_dao_aws_s3.get(tag=tag)

    def list_legislation_data(self, term_tag: TermTag):
        return self.legislation_dao_aws_s3.list(term_tag=term_tag)

    def fetch_legislation_data(self, tag: LegislationTag):
        return self.legislation_dao_aws_s3.get(tag=tag)

    def save(self, data: D) -> None:
        if isinstance(data, MemberData):
            self.member_dao_aws_s3.save(data=data)
        elif isinstance(data, MemberImageData):
            self.member_image_dao_aws_s3.save(data=data)

        elif isinstance(data, GroupData):
            self.group_dao_aws_s3.save(data=data)
        elif isinstance(data, GroupImageData):
            self.group_image_dao_aws_s3.save(data=data)

        elif isinstance(data, VotingData):
            self.voting_dao_aws_s3.save(data=data)
        elif isinstance(data, VotingOutcomeData):
            self.voting_outcome_dao_aws_s3.save(data=data)

        elif isinstance(data, Groups):
            self.groups_dao_aws_s3.save(data=data)
        elif isinstance(data, GroupsMembersRotation):
            self.groups_members_rotation_dao_aws_s3.save(data=data)
        elif isinstance(data, GroupsVotingsOutcomesDisciplineRanking):
            self.groups_votings_outcomes_discipline_ranking_dao_aws_s3.save(data=data)

        elif isinstance(data, StatementData):
            self.statement_dao_aws_s3.save(data=data)

        elif isinstance(data, LegislationData):
            self.legislation_dao_aws_s3.save(data=data)
        elif isinstance(data, LegislationStageData):
            self.legislation_stage_dao_aws_s3.save(data=data)
        elif isinstance(data, LegislationVotingData):
            self.legislation_voting_dao_aws_s3.save(data=data)

        elif isinstance(data, Members):
            self.members_dao_aws_s3.save(data=data)
        elif isinstance(data, MembersVotingsOutcomesAbstainRanking):
            self.members_voting_outcome_abstain_ranking_dao_aws_s3.save(data=data)
        elif isinstance(data, MembersVotingsOutcomesNoVotedRanking):
            self.members_voting_outcome_no_voted_ranking_dao_aws_s3.save(data=data)
        elif isinstance(data, MembersVotingsOutcomesRebelRanking):
            self.members_voting_outcome_rebel_ranking_dao_aws_s3.save(data=data)
        elif isinstance(data, MembersVotingsOutcomesStats):
            self.members_votings_outcomes_stats_dao_aws_s3.save(data=data)
        elif isinstance(data, MembersVotingsOutcomesConsistencyChamber):
            self.members_votings_outcomes_consistency_chamber_dao_aws_s3.save(data=data)
        elif isinstance(data, MembersVotingsOutcomesConsistencyGroups):
            self.members_votings_outcomes_consistency_groups_dao_aws_s3.save(data=data)

        elif isinstance(data, LegislationAnalytics):
            self.legislation_analytics_dao_aws_s3.save(data=data)
        elif isinstance(data, LegislationStagesAnalytics):
            self.legislation_stages_analytics_dao_aws_s3.save(data=data)
        elif isinstance(data, LegislationVotingsAnalytics):
            self.legislation_votings_analytics_dao_aws_s3.save(data=data)

        elif isinstance(data, VotingRollCallAnalytics):
            self.voting_roll_call_analytics_dao_aws_s3.save(data=data)

        else:
            raise S3RepositoryException(f"Save method - Not handle instance type {type(data)}")

    def bulk_save(self, data: List[D]) -> None:
        if isinstance(data[0], StatementData):
            self.statement_dao_aws_s3.bulk_save(data=data)

        else:
            raise S3RepositoryException(f"Bulk save method - Not handle instance type {type(data[0])}")
