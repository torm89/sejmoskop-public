from typing import List

from processing.models.dao.aws.s3.analytics import TagAnalyticsDaoAwsS3, TagTagsAnalyticsDaoAwsS3
from processing.models.data.analytics.legislation import LegislationAnalytics, LegislationStagesAnalytics, \
    LegislationVotingsAnalytics
from processing.models.tags import TermTag


class LegislationDaoAwsS3(TagTagsAnalyticsDaoAwsS3[TermTag, LegislationAnalytics]):
    """List of all processes (aggregate) plus one file per process."""

    @property
    def by_column_name(self) -> str:
        return 'legislation_number'

    @staticmethod
    def s3_key(tag: TermTag) -> str:
        return f"web/legislation/{tag.chamber_name}/{tag.term_id}/legislation.json"

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/legislation/{tag.chamber_name}/{tag.term_id}/{by}/legislation.json"


class LegislationStagesDaoAwsS3(TagAnalyticsDaoAwsS3[TermTag, LegislationStagesAnalytics]):
    """The stage timeline, one file per process (no aggregate)."""

    @property
    def by_column_name(self) -> List[str]:
        return ['legislation_number']

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/legislation/{tag.chamber_name}/{tag.term_id}/{by[0]}/legislation_stages.json"


class LegislationVotingsDaoAwsS3(TagAnalyticsDaoAwsS3[TermTag, LegislationVotingsAnalytics]):
    """The stage->vote links (with vote context), one file per process."""

    @property
    def by_column_name(self) -> List[str]:
        return ['legislation_number']

    @staticmethod
    def s3_key_by(tag: TermTag, by: str) -> str:
        return f"web/legislation/{tag.chamber_name}/{tag.term_id}/{by[0]}/legislation_votings.json"
