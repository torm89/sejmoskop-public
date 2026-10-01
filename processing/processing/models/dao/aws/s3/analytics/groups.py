from processing.models.dao import T
from processing.models.dao.aws.s3.analytics import TagsAnalyticsDaoAwsS3, TagTagsAnalyticsDaoAwsS3
from processing.models.data.analytics.groups import Groups, GroupsMembersRotation, \
    GroupsVotingsOutcomesDisciplineRanking
from processing.models.tags import TermTag


class GroupsDaoAwsS3(TagTagsAnalyticsDaoAwsS3[TermTag, Groups]):
    @property
    def by_column_name(self) -> str:
        return 'name'

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/groups/{tag.chamber_name}/{tag.term_id}/groups.json"

    @staticmethod
    def s3_key_by(tag: T, by: str) -> str:
        return f"web/groups/{tag.chamber_name}/{tag.term_id}/{by}/group.json"


class GroupsMembersRotationDaoAwsS3(TagsAnalyticsDaoAwsS3[TermTag, GroupsMembersRotation]):

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/groups/{tag.chamber_name}/{tag.term_id}/groups_members_rotation.json"


class GroupsVotingsOutcomesDisciplineRankingDaoAwsS3(
    TagsAnalyticsDaoAwsS3[TermTag, GroupsVotingsOutcomesDisciplineRanking]
):

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/groups/{tag.chamber_name}/{tag.term_id}/groups_votings_outcomes_discipline_ranking.json"
