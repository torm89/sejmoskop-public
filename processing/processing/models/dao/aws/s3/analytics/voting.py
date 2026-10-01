import asyncio
from typing import List

from processing.models.dao.aws.s3.analytics import TagAnalyticsDaoAwsS3
from processing.models.data import Data
from processing.models.data.analytics.voting import VotingRollCallAnalytics
from processing.models.tags import TermTag


class VotingRollCallDaoAwsS3(TagAnalyticsDaoAwsS3[TermTag, VotingRollCallAnalytics]):
    """Per-MP roll-call, one file per voting (no aggregate). The term-wide path
    reflects that this is no longer legislation-scoped."""

    @property
    def by_column_name(self) -> List[str]:
        return ['session_id', 'voting_id']

    @staticmethod
    def s3_key_by(tag: TermTag, by) -> str:
        return f"web/votings/{tag.chamber_name}/{tag.term_id}/{by[0]}/{by[1]}.json"

    def save(self, data: VotingRollCallAnalytics) -> None:
        # A voting's roll-call never changes once it happened, so only write
        # votings not already on the bucket: the first run exports everything,
        # later runs write just the new votings. (To force a full re-export —
        # e.g. after the export shape changes — clear the term's web/votings
        # prefix first.)
        prefix = f"web/votings/{data.tag.chamber_name}/{data.tag.term_id}/"
        existing = {
            obj.get("Key")
            for obj in self.provider.s3_list_objects(bucket_name=self.bucket_name, prefix=prefix)
        }

        objs = []
        for (by), df in self.group_by(data=data):
            key = self.s3_key_by(tag=data.tag, by=by)
            if key in existing:
                continue
            objs.append({
                "bucket_name": self.bucket_name,
                "key": key,
                "data": Data.df_to_json(df).encode('utf-8'),
            })

        if not objs:
            return

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.provider.s3_save_objects_bulk(objs=objs))
