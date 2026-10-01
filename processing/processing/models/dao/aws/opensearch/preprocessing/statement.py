# import os
# from typing import Dict, List
#
# from processing.models.dao import D, T
# from processing.models.dao.aws.opensearch import DaoAwsOpensearch
# from processing.models.data.processing.statement import StatementTimelineData
# from processing.models.tags import StatementTag, TermTag
#
#
# class StatementTimelineDaoAwsOpensearch(DaoAwsOpensearch[StatementTag, StatementTimelineData]):
#
#     @property
#     def opensearch_endpoint(self) -> str:
#         return os.environ.get("AWS_OPENSEARCH_SEJMOSKOP_ENDPOINT", "localhost:9200")
#
#     def initialize(self):
#         pass
#         # if not self.client.indices.exists_alias(name="sejmoskop-statements"):
#         #     self.client.indices.put_alias(index="sejmoskop-statements-*", name="sejmoskop-statements")
#
#     def opensearch_index(self, tag: StatementTag) -> str:
#         return f"sejmoskop-statements-{tag.chamber_name}-{tag.term_id}-{tag.session_id}-{tag.date_id}"
#
#     def document_id(self, tag: T, data: Dict) -> str:
#         return data['id']
#
#     def list(self, term_tag: TermTag) -> List[D]:
#         raise NotImplementedError
#
#     def get(self, tag: T) -> D:
#         raise NotImplementedError
