from processing.models.data import DataHot, DataNoSql
from processing.models.tags import StatementTag


class StatementHotData(DataHot):
    pass


class StatementData(DataNoSql[StatementTag]):
    pass
