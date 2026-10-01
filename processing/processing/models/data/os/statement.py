import json
from typing import Dict, List


def prepare_id(tag: Dict, timeline_id: int = None) -> str:
    _id = f"{tag['chamberName']}-{tag['termId']}-{tag['sessionId']}-{tag['dateId']}-{tag['statementIdNew']}"

    if timeline_id:
        _id += f"-{timeline_id}"

    return _id


def prepare_sort_field(tag: Dict, timeline_id: int = None) -> Dict:
    sort_field = {
        "term_id": int(tag['termId']),
        "session_id": int(tag['sessionId']),
        # dateId is "3" for sejm/senat and "YYYY-MM-DD" for the European
        # Parliament; stripping the dashes turns both into a sortable integer.
        "date_id": int(tag['dateId'].replace("-", "")),
        "statement_id_new": int(tag['statementIdNew'])
    }
    if timeline_id:
        sort_field['timeline_id'] = timeline_id

    return sort_field


def prepare_bulk_payload(document: Dict) -> List[str]:
    payload = []

    # Only the European Parliament carries a per-statement language (from the
    # source LG attribute); sejm/senat statements are always Polish.
    language = document.get('language') or 'PL'

    for record in document['timeline']:
        payload += [
            json.dumps({
                "update": {
                    "_index": 'statements-timeline-items',
                    "_id": prepare_id(document['tag'], record['timeline_id']),
                },
            }),
            json.dumps({
                "doc": {
                    "statement": {
                        "tag": document['tag'],
                        "speaker": document['speaker'],
                        "chairman": document['chairman'],
                        "details": document['details'],
                        "language": language,
                    },
                    **record,
                    "sort": prepare_sort_field(document['tag'], record['timeline_id']),
                },
                "doc_as_upsert": True
            })
        ]

    for i, item in enumerate(document['timeline']):
        if 'text_interpr' in item:
            item.pop('text_interpr')

            document['timeline'][i] = item

    payload += [
        json.dumps({
            "update": {
                "_index": 'statements',
                "_id": prepare_id(document['tag'])
            },
        }),
        json.dumps({
            "doc": {
                **document,
                "language": language,
                "sort": prepare_sort_field(document['tag']),
            },
            "doc_as_upsert": True
        })
    ]

    return payload
