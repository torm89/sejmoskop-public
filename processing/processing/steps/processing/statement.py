import os
from typing import List, Dict

from morfeusz2 import Morfeusz

from processing.models.data.preprocessing.statement import StatementData
from processing.models.tags import StatementTag
from processing.steps.step import Step
from processing.utils.concraft_pl.concraft_pl2 import Concraft


class StatementProcessingStep(Step):

    @classmethod
    def _morf_client(cls):
        return Morfeusz(expand_tags=True)

    @classmethod
    def _concraft_client(cls):
        port = os.environ.get('CONCRAFT_PORT', '3000')
        server_addr = os.environ.get('CONCRAFT_SERVER_ADDR', 'http://localhost')
        return Concraft(server_addr=server_addr, port=port)

    @classmethod
    def _prepare_statements_data_list(cls, statements: List[Dict]) -> List[StatementData]:
        return [
            StatementData.from_dict(tag=StatementTag(**statement['tag']), data=statement) for statement in statements
        ]
