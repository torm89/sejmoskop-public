import re
from typing import Dict, List

from processing.models.tags import LegislationTag


class LegislationProcessingTransformerSejm:
    """Splits one raw Sejm process into three flat row sets: the legislation
    row, its ordered stages, and the links from a stage to a roll-call vote."""

    @staticmethod
    def _clean(value) -> str:
        # The lake stores these rows as CSV read by OpenCSVSerde, which is
        # line-based: a newline inside a free-text field (a multi-line stage
        # name or decision) splits the record across physical lines and shifts
        # every later column. Collapse all whitespace to single spaces so each
        # record stays on one line.
        return re.sub(r"\s+", " ", str(value)).strip()

    @staticmethod
    def extract_legislation(tag: LegislationTag, data: Dict) -> Dict:
        return {
            "legislation_number": tag.legislation_number,
            "title": LegislationProcessingTransformerSejm._clean(data.get("title", "")),
            "document_type": data.get("documentType", ""),
            "passed": str(data.get("passed", "")),
            # The Sejm API spells this field "procesStartDate" (single s).
            "process_start_date": data.get("procesStartDate", ""),
            "change_date": data.get("changeDate", ""),
            "closure_date": data.get("closureDate", ""),
        }

    @staticmethod
    def _stage_print_numbers(stage: Dict) -> str:
        # Sejm print ("druk") numbers sit on the stage itself (e.g. the original
        # bill on the Start stage) and/or on its children (e.g. committee reports
        # and amendments). Collect all of them, in order, deduped, as a
        # comma-separated list so the web can link to every document.
        numbers = []
        if stage.get("printNumber"):
            numbers.append(str(stage["printNumber"]))
        for child in stage.get("children", []) or []:
            if child.get("printNumber"):
                numbers.append(str(child["printNumber"]))

        seen = set()
        unique = [n for n in numbers if not (n in seen or seen.add(n))]
        return ",".join(unique)

    @staticmethod
    def extract_stages(tag: LegislationTag, data: Dict) -> List[Dict]:
        stages = data.get("stages", []) or []

        rows = [
            {
                "legislation_number": tag.legislation_number,
                "stage_index": str(index),
                "stage_name": LegislationProcessingTransformerSejm._clean(stage.get("stageName", "")),
                "stage_type": stage.get("stageType", ""),
                "date": stage.get("date", ""),
                # Final stages carry `decision`; the Senate stage carries `position`.
                "decision": LegislationProcessingTransformerSejm._clean(
                    stage.get("decision", stage.get("position", ""))),
                "print_numbers": LegislationProcessingTransformerSejm._stage_print_numbers(stage),
            }
            for index, stage in enumerate(stages)
        ]

        # The promulgated act and its journal reference (e.g. "M.P. 2023 poz.
        # 1261" or "Dz.U. 2024 poz. 1615") are not in the API `stages` array —
        # they live in the process's top-level fields. The sejm.gov.pl timeline
        # shows that published act as its last node, so add it once the process
        # has passed and been announced. Bills (ustawy) already end with an "End"
        # stage, so just attach the journal reference to it; resolutions (uchwały)
        # have no closing stage at all, so append one.
        display_address = LegislationProcessingTransformerSejm._clean(data.get("displayAddress", ""))
        if str(data.get("passed", "")).lower() == "true" and display_address:
            if rows and rows[-1]["stage_type"] == "End":
                if not rows[-1]["decision"]:
                    rows[-1]["decision"] = display_address
            else:
                rows.append({
                    "legislation_number": tag.legislation_number,
                    "stage_index": str(len(rows)),
                    "stage_name": LegislationProcessingTransformerSejm._clean(data.get("titleFinal", "")),
                    "stage_type": "End",
                    "date": data.get("closureDate", ""),
                    "decision": display_address,
                    "print_numbers": "",
                })

        return rows

    @staticmethod
    def extract_votings(tag: LegislationTag, data: Dict) -> List[Dict]:
        stages = data.get("stages", []) or []

        votings = []
        for index, stage in enumerate(stages):
            for child in stage.get("children", []) or []:
                voting = child.get("voting")
                if not voting:
                    continue

                votings.append({
                    "legislation_number": tag.legislation_number,
                    "stage_index": str(index),
                    "session_id": str(voting["sitting"]),
                    "voting_id": str(voting["votingNumber"]),
                })

        return votings
