from processing.models.tags import LegislationTag
from processing.transformers.processing.sejm.legislation import LegislationProcessingTransformerSejm


def _tag():
    return LegislationTag(chamberName="sejm", termId="10", legislationNumber="30")


def test_extract_legislation():
    tag = _tag()
    data = {
        "chamberName": "sejm", "termId": "10", "legislationNumber": "30",
        "title": "Obywatelski projekt ustawy o zmianie ustawy o rencie socjalnej",
        "documentType": "projekt ustawy", "passed": True,
        # The Sejm API spells this field "procesStartDate" (single s).
        "procesStartDate": "2023-11-29", "changeDate": "2024-01-15", "closureDate": "",
    }

    assert LegislationProcessingTransformerSejm.extract_legislation(tag, data) == {
        "legislation_number": "30",
        "title": "Obywatelski projekt ustawy o zmianie ustawy o rencie socjalnej",
        "document_type": "projekt ustawy",
        "passed": "True",
        "process_start_date": "2023-11-29",
        "change_date": "2024-01-15",
        "closure_date": "",
    }


def test_extract_legislation_missing_fields_default_to_empty():
    tag = _tag()

    assert LegislationProcessingTransformerSejm.extract_legislation(tag, {}) == {
        "legislation_number": "30",
        "title": "",
        "document_type": "",
        "passed": "",
        "process_start_date": "",
        "change_date": "",
        "closure_date": "",
    }


def test_extract_stages_indexes_and_decision_fallback_to_position():
    tag = _tag()
    data = {
        "stages": [
            # print number from a child (committee report)
            {"stageName": "II czytanie", "stageType": "SejmReading", "date": "2023-12-10", "decision": "skierowano",
             "children": [{"printNumber": "583"}, {"printNumber": "583-A"}]},
            {"stageName": "Stanowisko Senatu", "stageType": "SenatePosition", "date": "2024-01-15",
             "position": "nie wniósł poprawek"},
            # print number on the stage itself (the original bill)
            {"stageName": "Projekt wpłynął do Sejmu", "stageType": "Start", "date": "2023-11-29",
             "printNumber": "30"},
        ]
    }

    assert LegislationProcessingTransformerSejm.extract_stages(tag, data) == [
        {"legislation_number": "30", "stage_index": "0", "stage_name": "II czytanie",
         "stage_type": "SejmReading", "date": "2023-12-10", "decision": "skierowano", "print_numbers": "583,583-A"},
        {"legislation_number": "30", "stage_index": "1", "stage_name": "Stanowisko Senatu",
         "stage_type": "SenatePosition", "date": "2024-01-15", "decision": "nie wniósł poprawek",
         "print_numbers": ""},
        {"legislation_number": "30", "stage_index": "2", "stage_name": "Projekt wpłynął do Sejmu",
         "stage_type": "Start", "date": "2023-11-29", "decision": "", "print_numbers": "30"},
    ]


def test_extract_stages_empty():
    assert LegislationProcessingTransformerSejm.extract_stages(_tag(), {}) == []


def test_extract_stages_collapses_newlines_in_free_text():
    # OpenCSVSerde reads the lake CSV line-by-line, so a newline inside a stage
    # name or decision splits the record and shifts every later column (this
    # crashed the legislation analytics: a decision tail landed in stage_index).
    tag = _tag()
    data = {
        "stages": [
            {"stageName": "Skierowano\n do komisji", "stageType": "Committee", "date": "2024-06-14",
             "decision": "przyjęto z poprawkami,\n uzupełnionym w dniu 14 czerwca 2024 r."},
        ]
    }

    stages = LegislationProcessingTransformerSejm.extract_stages(tag, data)
    assert stages[0]["stage_name"] == "Skierowano do komisji"
    assert stages[0]["decision"] == "przyjęto z poprawkami, uzupełnionym w dniu 14 czerwca 2024 r."


def test_extract_stages_appends_published_act_for_resolution():
    # Resolutions (uchwały) have no closing API stage; the published act lives in
    # the top-level fields and must be added as the final node.
    tag = _tag()
    data = {
        "passed": True,
        "titleFinal": "w sprawie ustalenia liczby wicemarszałków Sejmu",
        "displayAddress": "M.P. 2023 poz. 1261",
        "closureDate": "2023-11-13",
        "stages": [
            {"stageName": "Projekt wpłynął do Sejmu", "stageType": "Start", "date": "2023-11-13", "printNumber": "2"},
            {"stageName": "I czytanie na posiedzeniu Sejmu", "stageType": "SejmReading", "date": "2023-11-13",
             "decision": "podjęto uchwałę"},
        ],
    }

    stages = LegislationProcessingTransformerSejm.extract_stages(tag, data)
    assert len(stages) == 3
    assert stages[-1] == {
        "legislation_number": "30", "stage_index": "2",
        "stage_name": "w sprawie ustalenia liczby wicemarszałków Sejmu",
        "stage_type": "End", "date": "2023-11-13",
        "decision": "M.P. 2023 poz. 1261", "print_numbers": "",
    }


def test_extract_stages_attaches_journal_reference_to_existing_end_stage():
    # Bills (ustawy) already end with an "End" stage; reuse it and only attach the
    # journal reference rather than appending a duplicate node.
    tag = _tag()
    data = {
        "passed": True,
        "displayAddress": "Dz.U. 2024 poz. 1615",
        "closureDate": "2024-09-27",
        "stages": [
            {"stageName": "Prezydent podpisał ustawę", "stageType": "PresidentSignature", "date": "2024-09-20"},
            {"stageName": "Uchwalono", "stageType": "End", "date": "2024-09-27"},
        ],
    }

    stages = LegislationProcessingTransformerSejm.extract_stages(tag, data)
    assert len(stages) == 2
    assert stages[-1]["stage_type"] == "End"
    assert stages[-1]["decision"] == "Dz.U. 2024 poz. 1615"


def test_extract_stages_no_published_act_without_journal_reference():
    # Passed but not yet announced (no displayAddress) -> no final node added.
    tag = _tag()
    data = {
        "passed": True,
        "stages": [
            {"stageName": "I czytanie", "stageType": "SejmReading", "date": "2024-01-10", "decision": "podjęto uchwałę"},
        ],
    }

    stages = LegislationProcessingTransformerSejm.extract_stages(tag, data)
    assert len(stages) == 1
    assert stages[-1]["stage_type"] == "SejmReading"


def test_extract_votings_links_stage_to_vote():
    tag = _tag()
    data = {
        "stages": [
            {"stageType": "Start"},  # no children
            {"stageType": "SejmReading", "children": [
                {"stageType": "x"},  # child without a voting -> skipped
                {"voting": {"sitting": 18, "votingNumber": 30, "term": 10, "yes": 200}},
            ]},
        ]
    }

    assert LegislationProcessingTransformerSejm.extract_votings(tag, data) == [
        {"legislation_number": "30", "stage_index": "1", "session_id": "18", "voting_id": "30"},
    ]


def test_extract_votings_none_when_no_votes():
    data = {"stages": [{"stageType": "Start"}, {"stageType": "CommitteeWork", "children": []}]}

    assert LegislationProcessingTransformerSejm.extract_votings(_tag(), data) == []
