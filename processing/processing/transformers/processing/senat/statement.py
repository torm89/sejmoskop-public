import logging
import re
from typing import Dict, List

from morfeusz2 import Morfeusz

from processing.models.dao.aws.s3.preprocessing.statement import StatementHotDaoAwsS3
from processing.models.tags import StatementTag
from processing.transformers.processing.statement import StatementProcessingTransformer
from processing.utils.concraft_pl.concraft_pl2 import Concraft


class StatementProcessingTransformerSenat(StatementProcessingTransformer):

    @classmethod
    def _is_statement_link(cls, text: str) -> bool:
        return bool(re.match(r"^<Statement .+>$", text))

    @classmethod
    def _is_votings_link(cls, text: str) -> bool:
        return bool(re.match(r"^<VotingOutcomes .+>$", text))

    @classmethod
    def _enrich_statement_with_details(cls, statement: Dict, hot_dao: StatementHotDaoAwsS3):
        tag = StatementTag(**statement['tag'])
        statement_hot = hot_dao.get(tag)

        statement['details'] = statement_hot.get('details', {})

        return statement

    @classmethod
    def _enrich_statements_with_statement_details(cls, statements: List[Dict], hot_dao: StatementHotDaoAwsS3):
        logging.info("Enriching statements with statement details")

        for i, statement in enumerate(statements):
            if (i + 1) % 10 == 0 or i + 1 == len(statements):
                logging.info(
                    f"Processing statement {i + 1} of {len(statements)} ( {(i + 1) / len(statements) * 100:.2f}% )")

            statements[i] = cls._enrich_statement_with_details(statement, hot_dao)

        return statements

    @classmethod
    def _get_next_statement_tag(cls, text: str, tag: StatementTag, statement_id_new: int) -> StatementTag:
        r = re.search(r"^<Statement (?P<statementId>.+)>$", text)
        statement_id = r.group('statementId')
        return StatementTag(
            **tag.model_dump(by_alias=True, exclude={"statement_id", "statement_id_new"}),
            statementId=statement_id,
            statementIdNew=statement_id_new
        )

    @classmethod
    def enrich_statements(
            cls, statements: List[Dict], hot_dao: StatementHotDaoAwsS3, morf: Morfeusz, concraft: Concraft
    ) -> List[Dict]:
        statements = cls._enrich_statements_with_statement_details(statements, hot_dao)
        statements = cls._enrich_statements_with_interpretation(statements, morf, concraft)

        return statements

