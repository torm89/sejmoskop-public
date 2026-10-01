import datetime
import logging
import re
from typing import Dict, List

from morfeusz2 import Morfeusz

from processing.models.dao.aws.s3.preprocessing.statement import StatementHotDaoAwsS3
from processing.models.tags import StatementTag
from processing.transformers.processing.statement import StatementProcessingTransformer
from processing.utils.concraft_pl.concraft_pl2 import Concraft


class StatementProcessingTransformerSejm(StatementProcessingTransformer):

    @classmethod
    def _is_statement_link(cls, text: str) -> bool:
        return "wypowiedz.xsp?posiedzenie=" in text

    @classmethod
    def _is_votings_link(cls, text: str) -> bool:
        return "agent.xsp?symbol=glosowania" in text

    @classmethod
    def _extract_marshal_full_name(cls, statements: List[Dict]):
        for statement in statements:
            for record in statement.get('timeline', []):
                for comment in record.get('comments', []):
                    if comment.startswith("Na posiedzeniu"):
                        r = re.search(r"marszałek Sejmu (\w+\s[\w\-]+)", comment)
                        if r:
                            return r.group(1)

        logging.warning("Marshal full name not found")
        return ""

    @classmethod
    def _enrich_statements_with_the_marshal_full_name(cls, statements: List[Dict]):
        logging.info("Enriching statements with the marshal full name")

        marshal_full_name = cls._extract_marshal_full_name(statements)
        if marshal_full_name:
            for i, statement in enumerate(statements):
                for j, record in enumerate(statement.get('timeline', [])):
                    if 'speaking' in record and record['speaking']['name'] == 'Marszałek':
                        statements[i]['timeline'][j]['speaking']['name'] = f"Marszałek {marshal_full_name}"

                for key in ['chairman', 'speaker']:
                    if key in statement and statement[key]['name'] == 'Marszałek':
                        statements[i][key]['name'] = f"Marszałek {marshal_full_name}"

        return statements

    @classmethod
    def _extract_date(cls, statement: Dict) -> str:
        r = re.search(r'\d{2}-\d{2}-\d{4}', statement['title02'])
        date = datetime.datetime(1900, 1, 1) if not r else datetime.datetime.strptime(r.group(0), '%d-%m-%Y')

        return date.strftime("%Y-%m-%d")

    @classmethod
    def _enrich_statement_with_details(cls, statement: Dict, hot_dao: StatementHotDaoAwsS3):
        tag = StatementTag(**statement['tag'])
        statement_hot = hot_dao.get(tag)

        statement['details'] = {
            "date": cls._extract_date(statement=statement_hot),
            "description_01": statement_hot['description01'],
            "description_02": statement_hot['description02'],
            "title_01": statement_hot['title01'],
            "title_02": statement_hot['title02'],
            "video_url": statement_hot['videoUrl']
        }

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
        r = re.search(r"wyp=(?P<statementId>\d+)$", text)
        statement_id = str(int(r.group('statementId')))
        return StatementTag(
            **tag.model_dump(by_alias=True, exclude={"statement_id", "statement_id_new"}),
            statementId=statement_id,
            statementIdNew=statement_id_new
        )

    @classmethod
    def enrich_statements(
            cls, statements: List[Dict], hot_dao: StatementHotDaoAwsS3, morf: Morfeusz, concraft: Concraft
    ) -> List[Dict]:
        statements = cls._enrich_statements_with_the_marshal_full_name(statements)
        statements = cls._enrich_statements_with_statement_details(statements, hot_dao)
        statements = cls._enrich_statements_with_interpretation(statements, morf, concraft)

        return statements
