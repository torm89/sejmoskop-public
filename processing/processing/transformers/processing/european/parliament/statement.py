import asyncio
import html
import logging
from typing import Dict, List

from morfeusz2 import Morfeusz

from processing.models.tags import StatementTag
from processing.transformers.processing.statement import StatementProcessingTransformer, StatementTextType
from processing.utils.concraft_pl.concraft_pl2 import Concraft


class StatementProcessingTransformerEuropeanParliament(StatementProcessingTransformer):

    @classmethod
    def extract_timeline(cls, tag: StatementTag, statement: Dict) -> Dict:
        logging.info(f"Extracting statements for {tag.model_dump()}")

        paras = statement['data']['intervention'].get('PARA', [])
        if not isinstance(paras, list):
            paras = [paras]

        timeline = []
        for i, line in enumerate(paras):
            if isinstance(line, str):
                text = line
            elif isinstance(line, dict) and '#text' in line:
                text = line['#text']
            else:
                text = ""
                logging.warning(f"Unknown line type, {statement}")

            # europarl double-escapes entities in the verbatim XML (e.g. a
            # non-break space arrives as "&amp;#xa0;"). fast-xml-parser undoes
            # only the outer "&amp;", leaving a literal "&#xa0;" in the text, so
            # decode that leftover entity layer here.
            text = html.unescape(text)

            timeline.append({
                "text": text,
                "comments": [],
                "text_type": StatementTextType.NORMAL,
                "timeline_id": i,
            })

        return {"timeline": timeline}

    @classmethod
    def encode_statement_id(cls, statement_id: str) -> int:
        # statementId is "<agenda item>-<intervention>". The agenda item may
        # carry a sub-level (e.g. "9.10"). Pack item, sub-item and intervention
        # into fixed 3-digit slots so statementIdNew is an int, unique within the
        # session day and sortable in agenda order (item, sub-item, intervention).
        item, intervention = statement_id.rsplit('-', 1)
        major, _, minor = item.partition('.')
        return (int(major) * 1000 + int(minor or 0)) * 1000 + int(intervention)

    @classmethod
    def extract_tag(cls, tag: StatementTag, statement: Dict) -> Dict:
        return {
            "tag": {
                "chamberName": statement['chamberName'],
                "termId": statement['termId'],
                "sessionId": statement['sessionId'],
                "dateId": statement['dateId'],
                "statementId": statement['statementId'],
                "statementIdNew": cls.encode_statement_id(statement['statementId']),
            }
        }

    @classmethod
    def extract_speaker(cls, tag: StatementTag, statement: Dict) -> Dict:
        speaker_name = statement['data']['intervention']['ORATEUR']['@_LIB'].replace("| ", "")
        return {
            "speaker": {
                "name": speaker_name,
                "member_tag": {
                    "chamberName": statement['chamberName'],
                    "termId": statement['termId'],
                    "memberId": statement['data']['intervention']['ORATEUR']['@_MEPID'],
                }
            }
        }

    @classmethod
    def _is_chairman_intervention(cls, orateur: Dict) -> bool:
        # The presiding officer's interventions carry no SPEAKER_TYPE (unlike the
        # Council/Commission/group speakers) and their EMPHAS label is the
        # presidency role in the speaker's own language ("Presidente. –",
        # "Der Präsident. –", "Πρόεδρος. –", "President."). A floor speaker's
        # EMPHAS label instead always carries a parenthetical country/affiliation
        # slot (e.g. "Laura Ferrara ()."), so the absence of "(" marks the chair.
        # This holds across languages, alphabets, and the term-9 ("@_LIB" is the
        # name) / term-10 ("@_LIB" is the role) format change.
        if orateur.get('@_SPEAKER_TYPE'):
            return False

        emphasis = orateur.get('EMPHAS')
        if isinstance(emphasis, list):
            emphasis = emphasis[0] if emphasis else None
        # fast-xml-parser coerces a purely numeric label to an int, so stringify.
        label = str(emphasis.get('#text', '')) if isinstance(emphasis, dict) else ''
        return bool(label) and '(' not in label

    @classmethod
    def extract_chairman(cls, tag: StatementTag, statement: Dict) -> Dict:
        orateur = statement['data']['intervention']['ORATEUR']
        if cls._is_chairman_intervention(orateur):
            # Mirror sejm/senat: the chair's own turn has speaker == chairman.
            return {"chairman": cls.extract_speaker(tag, statement)['speaker']}
        return {"chairman": {"name": ""}}

    # "Explanation of vote in writing" markers. term 9 tags these on the ORATEUR
    # via SPEAKER_TYPE ("ecrit", language-independent). term 10 dropped that and
    # instead opens the first PARA with an italic EMPHAS carrying the role in the
    # speaker's own language; written contributions use the localized "in
    # writing" phrase below. Forms for bg/cs/de/el/en/es/et/fi/hu/it/lt/mt/nl/pl/
    # pt/ro/sk/sl were observed in the verbatim reports; da/fr/ga/hr/lv/sv use the
    # official term (no occurrence seen in the sampled sittings yet).
    _WRITTEN_PHRASES = {
        "в писмена форма", "písemně", "skriftlig", "schriftlich", "kirjalikult",
        "γραπτώς", "in writing", "por escrito", "par écrit", "i scríbhinn",
        "u pisanom obliku", "per iscritto", "rakstiski", "raštu", "írásban",
        "bil-miktub", "schriftelijk", "na piśmie", "în scris", "písomne", "pisno",
        "kirjallinen",
    }

    @classmethod
    def _is_written_intervention(cls, intervention: Dict) -> bool:
        orateur = intervention['ORATEUR']

        speaker_type = orateur.get('@_SPEAKER_TYPE')
        if speaker_type:
            # term 9: the explicit, language-independent written marker.
            return speaker_type.lower() == 'ecrit'

        # term 10: the first PARA opens with an italic role label in the
        # speaker's language; a written contribution uses the "in writing" phrase.
        paras = intervention.get('PARA', [])
        if not isinstance(paras, list):
            paras = [paras]
        first = paras[0] if paras else None
        if not isinstance(first, dict):
            return False

        emphasis = first.get('EMPHAS')
        if isinstance(emphasis, list):
            emphasis = emphasis[0] if emphasis else None
        if not isinstance(emphasis, dict) or emphasis.get('@_NAME') != 'I':
            return False

        # fast-xml-parser coerces a purely numeric label (e.g. an italicised
        # "1984") to an int, so stringify before normalising.
        label = ' '.join(str(emphasis.get('#text') or '').split()).lower()
        return label in cls._WRITTEN_PHRASES

    @classmethod
    def extract_written(cls, tag: StatementTag, statement: Dict) -> Dict:
        return {"is_written": cls._is_written_intervention(statement['data']['intervention'])}

    @classmethod
    def extract_language(cls, tag: StatementTag, statement: Dict) -> Dict:
        return {
            "language": statement['data']['intervention']['ORATEUR']['LG'],
        }

    @classmethod
    def add_text_interpretation(cls, statement: Dict, morf: Morfeusz, concraft: Concraft) -> Dict:
        logging.info("Add text interpretation to statements for European Parliament")

        if statement['language'] == 'PL':
            loop = asyncio.get_event_loop()
            task = loop.create_task(cls._stem_statement(statement, morf, concraft))
            loop.run_until_complete(asyncio.gather(task))

            statement = task.result()

        return statement
