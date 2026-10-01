# from processing.models.dao import D
# from processing.models.dao.aws.opensearch.processing.statement import StatementTimelineDaoAwsOpensearch
# from processing.models.data.processing.statement import StatementTimelineData
#
#
# class OpensearchRepository:
#     def __init__(self):
#         self.statement_timeline_dao_aws_opensearch = StatementTimelineDaoAwsOpensearch()
#
#     def save(self, data: D) -> None:
#         if isinstance(data, StatementTimelineData):
#             self.statement_timeline_dao_aws_opensearch.save(data=data)
#
#         else:
#             raise Exception("Not handle instance type {}".format(type(data)))
