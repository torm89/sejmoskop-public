import json

from processing.transformers.processing.european.parliament.statement import \
    StatementProcessingTransformerEuropeanParliament


def test_encode_statement_id_handles_agenda_sub_items():
    encode = StatementProcessingTransformerEuropeanParliament.encode_statement_id

    # Plain agenda items keep item, sub-item and intervention in 3-digit slots.
    assert encode("12-9") == 12000009
    assert encode("3-39") == 3000039

    # A sub-item ("9.10") must not crash and must sort after item 9's
    # interventions but before item 10.
    assert encode("9-31") < encode("9.10-0") < encode("10-1")


def _orateur_statement(orateur: dict) -> dict:
    return {
        "chamberName": "european-parliament",
        "termId": "9",
        "data": {"intervention": {"ORATEUR": orateur}},
    }


def test_extract_chairman_marks_the_presiding_officer():
    extract = StatementProcessingTransformerEuropeanParliament.extract_chairman

    # term-9 shape: @_LIB is the name, EMPHAS is the role in the speaker's language.
    chair = _orateur_statement({
        "@_LIB": "Pina | Picierno",
        "@_MEPID": "124846",
        "EMPHAS": {"#text": "Presidente. –", "@_NAME": "B"},
    })
    chairman = extract(tag=None, statement=chair)["chairman"]
    assert chairman["name"] == "Pina Picierno"
    assert chairman["member_tag"]["memberId"] == "124846"

    # term-10 shape: @_LIB is the role itself, the person is only the MEPID.
    chair_t10 = _orateur_statement({
        "@_LIB": "President",
        "@_MEPID": "125042",
        "EMPHAS": {"#text": "President.", "@_NAME": "B"},
    })
    chairman_t10 = extract(tag=None, statement=chair_t10)["chairman"]
    assert chairman_t10["name"] == "President"
    assert chairman_t10["member_tag"]["memberId"] == "125042"


def test_extract_chairman_ignores_regular_speakers():
    extract = StatementProcessingTransformerEuropeanParliament.extract_chairman

    # A plain MEP: no SPEAKER_TYPE, but the EMPHAS label carries the "()" slot.
    mep = _orateur_statement({
        "@_LIB": "Laura | Ferrara",
        "@_MEPID": "124833",
        "EMPHAS": {"#text": "Laura Ferrara ().", "@_NAME": "B"},
    })
    assert extract(tag=None, statement=mep)["chairman"] == {"name": ""}

    # A non-Latin-script MEP: the role rule must not misfire just because the
    # Latin surname is absent from the native-script label.
    mep_greek = _orateur_statement({
        "@_LIB": "Giorgos | Georgiou",
        "@_MEPID": "197699",
        "EMPHAS": {"#text": "Γιώργος Γεωργίου ().", "@_NAME": "B"},
    })
    assert extract(tag=None, statement=mep_greek)["chairman"] == {"name": ""}

    # A group/Council/Commission speaker: SPEAKER_TYPE is set.
    group = _orateur_statement({
        "@_LIB": "Siegfried | Mureşan",
        "@_MEPID": "124802",
        "@_SPEAKER_TYPE": "au nom du groupe",
        "EMPHAS": {"#text": "Siegfried Mureşan,", "@_NAME": "B"},
    })
    assert extract(tag=None, statement=group)["chairman"] == {"name": ""}

    # A speaker with no EMPHAS label at all is never the chair.
    no_label = _orateur_statement({
        "@_LIB": "Josep | Borrell Fontelles",
        "@_MEPID": "96739",
        "@_SPEAKER_TYPE": "vpc/hr",
    })
    assert extract(tag=None, statement=no_label)["chairman"] == {"name": ""}


def _written_statement(orateur: dict, paras=None) -> dict:
    intervention = {"ORATEUR": orateur}
    if paras is not None:
        intervention["PARA"] = paras
    return {"data": {"intervention": intervention}}


def test_extract_written_term9_speaker_type():
    extract = StatementProcessingTransformerEuropeanParliament.extract_written

    # term 9: the explicit "ecrit" SPEAKER_TYPE, language-independent.
    written = _written_statement({"@_LIB": "Carlos | Zorrinho", "@_SPEAKER_TYPE": "ecrit"})
    assert extract(tag=None, statement=written)["is_written"] is True

    # Any other SPEAKER_TYPE is a spoken contribution.
    spoken = _written_statement({"@_LIB": "Petar | Vitanov", "@_SPEAKER_TYPE": "au nom du groupe"})
    assert extract(tag=None, statement=spoken)["is_written"] is False


def test_extract_written_term10_localized_phrase():
    extract = StatementProcessingTransformerEuropeanParliament.extract_written

    # term 10: no SPEAKER_TYPE; the first PARA opens with the localized
    # "in writing" phrase in italics. Check a couple of languages.
    for phrase in ("na piśmie", "in writing", "por escrito", "bil-miktub"):
        stmt = _written_statement(
            {"@_LIB": "X | Y"},
            paras=[{"EMPHAS": [{"#text": phrase, "@_NAME": "I"}, {"#text": ".", "@_NAME": "B"}],
                    "#text": " some written text"}],
        )
        assert extract(tag=None, statement=stmt)["is_written"] is True, phrase


def test_extract_written_ignores_non_written_italics():
    extract = StatementProcessingTransformerEuropeanParliament.extract_written

    # A blue-card exchange also opens with an italic label, but not a written one.
    blue_card = _written_statement(
        {"@_LIB": "X | Y"},
        paras=[{"EMPHAS": [{"#text": "blue-card question", "@_NAME": "I"}], "#text": " text"}],
    )
    assert extract(tag=None, statement=blue_card)["is_written"] is False

    # A plain spoken intervention whose first PARA is just text.
    spoken = _written_statement({"@_LIB": "X | Y"}, paras=[{"#text": "– Mr President, ..."}])
    assert extract(tag=None, statement=spoken)["is_written"] is False

    # fast-xml-parser turns a purely numeric italic (e.g. "1984") into an int;
    # detection must not crash on it.
    numeric = _written_statement(
        {"@_LIB": "X | Y"},
        paras=[{"EMPHAS": [{"#text": 1984, "@_NAME": "I"}], "#text": " text"}],
    )
    assert extract(tag=None, statement=numeric)["is_written"] is False


def test_extract_timeline_9_2024_03_12_10_5(
        statements_9_2024_03_12_10_5, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_10_5

    timeline = StatementProcessingTransformerEuropeanParliament.extract_timeline(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_timeline_9_2024_03_12_10_5.json"
    # reference_data_path.open('w+').write(json.dumps(timeline, indent=4))

    assert timeline == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_timeline_9_2024_03_12_12_9(
        statements_9_2024_03_12_12_9, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_12_9

    timeline = StatementProcessingTransformerEuropeanParliament.extract_timeline(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_timeline_9_2024_03_12_12_9.json"
    # reference_data_path.open('w+').write(json.dumps(timeline, indent=4))

    assert timeline == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_tag_9_2024_03_12_10_5(
        statements_9_2024_03_12_10_5, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_10_5

    tag = StatementProcessingTransformerEuropeanParliament.extract_tag(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_tag_9_2024_03_12_10_5.json"
    # reference_data_path.open('w+').write(json.dumps(tag, indent=4))

    assert tag == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_tag_9_2024_03_12_12_9(
        statements_9_2024_03_12_12_9, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_12_9

    tag = StatementProcessingTransformerEuropeanParliament.extract_tag(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_tag_9_2024_03_12_12_9.json"
    # reference_data_path.open('w+').write(json.dumps(tag, indent=4))

    assert tag == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_speaker_9_2024_03_12_10_5(
        statements_9_2024_03_12_10_5, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_10_5

    speaker = StatementProcessingTransformerEuropeanParliament.extract_speaker(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_speaker_9_2024_03_12_10_5.json"
    # reference_data_path.open('w+').write(json.dumps(speaker, indent=4))

    assert speaker == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_speaker_9_2024_03_12_12_9(
        statements_9_2024_03_12_12_9, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_12_9

    speaker = StatementProcessingTransformerEuropeanParliament.extract_speaker(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_speaker_9_2024_03_12_12_9.json"
    # reference_data_path.open('w+').write(json.dumps(speaker, indent=4))

    assert speaker == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_language_9_2024_03_12_10_5(
        statements_9_2024_03_12_10_5, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_10_5

    language = StatementProcessingTransformerEuropeanParliament.extract_language(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_language_9_2024_03_12_10_5.json"
    # reference_data_path.open('w+').write(json.dumps(language, indent=4))

    assert language == json.load(reference_data_path.open(encoding='utf-8'))


def test_extract_language_9_2024_03_12_12_9(
        statements_9_2024_03_12_12_9, reference_european_parliament_transformers_processing_path):
    statement, tag = statements_9_2024_03_12_12_9

    language = StatementProcessingTransformerEuropeanParliament.extract_language(tag=tag, statement=statement)

    reference_data_path = reference_european_parliament_transformers_processing_path / "statement_language_9_2024_03_12_12_9.json"
    # reference_data_path.open('w+').write(json.dumps(language, indent=4))

    assert language == json.load(reference_data_path.open(encoding='utf-8'))
