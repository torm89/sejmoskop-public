import asyncio
import logging
import re
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Dict, List

from botocore.exceptions import ClientError as BotoClientError
from morfeusz2 import Morfeusz
from pydantic import BaseModel

from processing.models.dao.aws.s3.preprocessing.statement import StatementHotDaoAwsS3
from processing.models.tags import StatementTag
from processing.utils.concraft_pl.concraft_pl2 import Concraft


class StatementTextType:
    INITIAL_COMMENT = "COMMENT"
    INTERJECTION = "INTERJECTION"
    COMMENT = "COMMENT"
    CHAIRMAN_ON = "CHAIRMAN_ON"
    CHAIRMAN_SWITCH = "CHAIRMAN_SWITCH"
    SPEAKER_ON = "SPEAKER_ON"
    NEXT_STATEMENT = "NEXT_STATEMENT"
    VOTINGS = "VOTINGS"
    NORMAL = "NORMAL"


class InterjectionTextType:
    NORMAL = "NORMAL"
    CHAIRMAN = "CHAIRMAN"


@dataclass(init=False)
class Statement:
    tag: Dict
    speaker: Dict = field(default_factory=dict)
    chairman: Dict = field(default_factory=dict)
    timeline: List[Dict] = field(default_factory=list)

    def __init__(self, tag: Dict, speaker: str = None, chairman: str = None, timeline: List[Dict] = None):
        self.tag = tag
        self.speaker = {'name': speaker if speaker else ''}
        self.chairman = {'name': chairman if chairman else ''}
        self.timeline = timeline if timeline else []


class Interpr(BaseModel):
    segment: str
    lemma: str
    morphosyntactic_tag: str
    labels: List[str]
    probability: float
    end_of_sentence: bool


class StatementProcessingTransformer(ABC):

    # Marks a contribution submitted to the record but not delivered orally.
    UNSPOKEN_COMMENT = "tekst niewygłoszony"

    @classmethod
    def _remove_brackets(cls, text: str) -> str:
        r = re.search(r"^\((.*)\)$", text)
        return r.group(1).strip() if r else text

    @classmethod
    def _remove_colon(cls, text: str) -> str:
        return text.replace(":", "").strip()

    @classmethod
    def _is_interjection(cls, text: str) -> bool:
        return text.startswith("(") and text.endswith(")") and ":" in text

    @classmethod
    def _is_comment(cls, text: str) -> bool:
        return text.startswith("(") and text.endswith(")") and not cls._is_interjection(text)

    @classmethod
    def _is_chairman_on(cls, text: str, chairman: str) -> bool:
        return text == f"{chairman}:"

    @classmethod
    def _is_speaker_on(cls, text: str, speaker: str) -> bool:
        return text == f"{speaker}:"

    @classmethod
    def _is_chairman_switch(cls, text: str) -> bool:
        return (text.startswith("Marszałek") or text.startswith("Wicemarszałek")) and len(text) < 80 and text[-1] == ":"

    @classmethod
    @abstractmethod
    def _is_statement_link(cls, text: str) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _is_votings_link(cls, text: str) -> bool:
        raise NotImplementedError

    @classmethod
    def _extract_text_type(cls, text: str, chairman: str, speaker: str) -> (str, str):
        if cls._is_statement_link(text):
            return StatementTextType.NEXT_STATEMENT, text
        elif cls._is_votings_link(text):
            return StatementTextType.VOTINGS, text
        elif cls._is_interjection(text):
            return StatementTextType.INTERJECTION, cls._remove_brackets(text)
        elif cls._is_comment(text):
            return StatementTextType.COMMENT, cls._remove_brackets(text)
        elif cls._is_chairman_on(text, chairman):
            return StatementTextType.CHAIRMAN_ON, cls._remove_colon(text)
        elif cls._is_speaker_on(text, speaker):
            return StatementTextType.SPEAKER_ON, cls._remove_colon(text)
        elif cls._is_chairman_switch(text):
            return StatementTextType.CHAIRMAN_SWITCH, cls._remove_colon(text)

        return StatementTextType.NORMAL, text

    @classmethod
    @abstractmethod
    def _get_next_statement_tag(cls, text: str, tag: StatementTag, statement_id_new: int) -> StatementTag:
        raise NotImplementedError

    @classmethod
    def _process_interjection(cls, text: str, timeline_id: int) -> Dict:
        speaking, interjection = text.split(':', 1)
        return {
            "speaking": {'name': speaking.strip()},
            "text": interjection.strip(),
            "text_type": StatementTextType.INTERJECTION,
            "text_subtype": InterjectionTextType.NORMAL,
            "timeline_id": timeline_id
        }

    @classmethod
    def _process_chairman_interjection(cls, text: str, chairman: str, timeline_id: int) -> Dict:
        return {
            "speaking": {'name': chairman},
            "text": text.strip(),
            "text_type": StatementTextType.INTERJECTION,
            "text_subtype": InterjectionTextType.CHAIRMAN,
            "timeline_id": timeline_id
        }

    @classmethod
    def _process_comment(cls, text: str, speaking: str, speaker: str, timeline_id: int) -> Dict:
        return {
            "text": "",
            "comments": [text.strip()],
            "text_type": StatementTextType.NORMAL,
            "timeline_id": timeline_id,
            **({"speaking": {'name': speaking}} if speaking != speaker else {}),
        }

    @classmethod
    def _extract_comments(cls, text: str) -> List[str]:
        return re.findall(r"\((.*?)\)", text)

    @classmethod
    def _process_normal_text(cls, text: str, timeline_id: int) -> Dict:
        return {
            "text": text.strip(),
            "comments": cls._extract_comments(text),
            "text_type": StatementTextType.NORMAL,
            "timeline_id": timeline_id
        }

    @classmethod
    def _add_text_unspoken_comment(cls, next_statement: List[Dict]) -> List[Dict]:
        next_statement[0]['timeline'].insert(
            0, {
                "text": "",
                "comments": [cls.UNSPOKEN_COMMENT],
                "text_type": StatementTextType.NORMAL,
                "timeline_id": -1
            }
        )
        return next_statement

    @classmethod
    def _append_statement(cls, statements: List, statement: Statement, chairman, speaker):
        if not statement.tag["statementIdNew"] or statement.tag["statementIdNew"] == -1:
            statement.tag["statementIdNew"] = len(statements)
        statement.speaker = {'name': speaker}
        statement.chairman = {'name': chairman}

        statements.append(statement.__dict__)

    @classmethod
    def _process_statement(cls, tag: StatementTag, records: List, chairman, speaker, statement_hot_dao):
        statements, timeline_id, speaking = [], 0, ""
        statement = Statement(tag=tag.model_dump(by_alias=True))

        for i, record in enumerate(records):
            if tag.statement_id_new == -1 and ((i + 1) % 100 == 0 or i + 1 == len(records)):
                logging.info(f"Processing record {i + 1} of {len(records)} ( {(i + 1) / len(records) * 100:.2f}% )")

            text_type, text = cls._extract_text_type(record, chairman, speaker)

            if text_type == StatementTextType.NEXT_STATEMENT:
                if statement.timeline:
                    cls._append_statement(
                        statements=statements, statement=statement, chairman=chairman, speaker=speaker)
                statement = Statement(tag=tag.model_dump(by_alias=True))

                next_statement_tag = cls._get_next_statement_tag(text=text, tag=tag, statement_id_new=len(statements))
                try:
                    next_statement_records = statement_hot_dao.get(next_statement_tag)["records"]
                except BotoClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchKey':
                        raise
                    # The Sejm site sometimes links to a statement that is missing
                    # from its own statement list (and the official API), so it was
                    # never scraped. Skip it instead of failing the whole day; the
                    # MISSING_STATEMENT marker feeds a CloudWatch alarm.
                    logging.warning(f"MISSING_STATEMENT - linked statement was never scraped, "
                                    f"skipping: {next_statement_tag.model_dump()}")
                    continue
                next_statement_speaker = cls._remove_colon(next_statement_records[0])

                is_text_unspoken = "(tekst niewygłoszony)" in next_statement_speaker
                if is_text_unspoken:
                    next_statement_speaker = next_statement_speaker.replace("(tekst niewygłoszony)", "").strip()

                next_statement = cls._process_statement(
                    tag=next_statement_tag, records=next_statement_records[1:], chairman=chairman,
                    speaker=next_statement_speaker, statement_hot_dao=statement_hot_dao,
                )

                if is_text_unspoken:
                    next_statement = cls._add_text_unspoken_comment(next_statement)

                statements.append(next_statement[0])
            elif text_type == StatementTextType.CHAIRMAN_SWITCH:
                chairman = speaker = speaking = text
            elif text_type == StatementTextType.CHAIRMAN_ON:
                speaking = chairman
            elif text_type == StatementTextType.SPEAKER_ON:
                speaking = speaker
            elif text_type == StatementTextType.VOTINGS:
                # TODO: To be implemented
                pass
            else:
                if text_type == StatementTextType.INTERJECTION:
                    interjection = cls._process_interjection(text=text, timeline_id=timeline_id)
                    statement.timeline.append(interjection)
                elif text_type == StatementTextType.COMMENT:
                    comment = cls._process_comment(
                        text=text, speaking=speaking, speaker=speaker, timeline_id=timeline_id
                    )
                    statement.timeline.append(comment)
                elif text_type == StatementTextType.NORMAL and speaker and speaking == chairman and speaker != chairman:
                    chairman_interjection = cls._process_chairman_interjection(
                        text=text, chairman=chairman, timeline_id=timeline_id
                    )
                    statement.timeline.append(chairman_interjection)
                elif text_type == StatementTextType.NORMAL:
                    normal_text = cls._process_normal_text(text, timeline_id=timeline_id)
                    statement.timeline.append(normal_text)

                timeline_id += 1

        cls._append_statement(statements=statements, statement=statement, chairman=chairman, speaker=speaker)

        return statements

    @classmethod
    async def _stem_text(cls, text: str, morf: Morfeusz, concraft: Concraft) -> List[Dict]:
        dag = morf.analyse(text)
        dag_disamb = await concraft.disamb_async(dag)

        interprs = []
        for data in dag_disamb:
            if data and data[-1] and data[-1] == "disamb":
                interpr = Interpr(**{
                    "segment": data[2][0],
                    "lemma": data[2][1],
                    "morphosyntactic_tag": data[2][2],
                    "labels": data[2][3],
                    "probability": float(data[3]),
                    "end_of_sentence": True if data[4] == "eos" else False
                })
                interprs.append(interpr.model_dump())

        return interprs

    @classmethod
    def _get_text_without_comments(cls, record: Dict) -> str:
        text = f"{record['text']}"
        for comment in record.get('comments', []):
            text = re.sub(fr"\s?\({comment}\)\s?", "", text)
        return text

    @classmethod
    async def _stem_statement(cls, statement: Dict, morf: Morfeusz, concraft: Concraft) -> Dict:
        for i, record in enumerate(statement['timeline']):
            if record['text']:
                text = StatementProcessingTransformer._get_text_without_comments(record)
                statement['timeline'][i]['text_interpr'] = \
                    await StatementProcessingTransformer._stem_text(text=text, morf=morf, concraft=concraft)

        return statement

    @classmethod
    def _enrich_statements_with_interpretation(
            cls, statements: List[Dict], morf: Morfeusz, concraft: Concraft) -> List[Dict]:
        logging.info("Enriching statements with interpretation")

        for i, statement in enumerate(statements):
            if (i + 1) % 10 == 0 or i + 1 == len(statements):
                logging.info(
                    f"Processing statement {i + 1} of {len(statements)} ( {(i + 1) / len(statements) * 100:.2f}% )")

            loop = asyncio.get_event_loop()
            task = loop.create_task(StatementProcessingTransformer._stem_statement(statement, morf, concraft))
            loop.run_until_complete(asyncio.gather(task))

            statements[i] = task.result()

        return statements

    @classmethod
    def extract_statements(cls, tag: StatementTag, proceedings: Dict, hot_dao: StatementHotDaoAwsS3) -> List[Dict]:
        logging.info(f"Extracting statements for {tag.model_dump()}")
        statements, speaker, chairman = [], "", ""
        records = proceedings['records']

        statements = cls._process_statement(
            tag=tag, records=records, chairman=chairman, speaker=speaker, statement_hot_dao=hot_dao
        )

        # Unify with the European Parliament: expose a document-level is_written
        # flag, here derived from the "tekst niewygłoszony" timeline marker.
        for statement in statements:
            statement['is_written'] = any(
                cls.UNSPOKEN_COMMENT in record.get('comments', [])
                for record in statement['timeline']
            )

        return statements

    @classmethod
    @abstractmethod
    def enrich_statements(
            cls, statements: List[Dict], hot_dao: StatementHotDaoAwsS3, morf: Morfeusz, concraft: Concraft
    ) -> List[Dict]:
        raise NotImplementedError
