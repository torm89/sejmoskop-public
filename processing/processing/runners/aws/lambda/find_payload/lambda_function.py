import logging

from processing.manager.batch.group import BatchManagerProcessingGroup, BatchManagerScrapeGroup
from processing.manager.batch.member import BatchManagerScrapeMember, BatchManagerProcessingMember
from processing.manager.batch.statement import BatchManagerScrapeStatement, BatchManagerProcessingStatement
from processing.manager.batch.voting import BatchManagerProcessingVoting, BatchManagerScrapeVoting
from processing.manager.batch.legislation import BatchManagerScrapeLegislation, BatchManagerProcessingLegislation

logger = logging.getLogger()
logger.setLevel("INFO")


class UnknownKindException(Exception):
    pass


def get_manager(kind: str):
    if kind == "scrape-member":
        return BatchManagerScrapeMember()
    elif kind == "scrape-voting":
        return BatchManagerScrapeVoting()
    elif kind == "scrape-group":
        return BatchManagerScrapeGroup()
    elif kind == "scrape-statements":
        return BatchManagerScrapeStatement()
    elif kind == "processing-member":
        return BatchManagerProcessingMember()
    elif kind == "processing-voting":
        return BatchManagerProcessingVoting()
    elif kind == "processing-group":
        return BatchManagerProcessingGroup()
    elif kind == "processing-statements":
        return BatchManagerProcessingStatement()
    elif kind == "scrape-legislation":
        return BatchManagerScrapeLegislation()
    elif kind == "processing-legislation":
        return BatchManagerProcessingLegislation()

    raise UnknownKindException(f"Unknown kind: {kind}")


def handler(event, context):
    payload_id, kind = event['payloadId'], event['kind']

    manager = get_manager(kind=kind)

    payload = manager.find_payload(payload_id=payload_id)
    payload_dumped_chunked = manager.dump_and_chunk_tags(tags=payload)

    manager.save_payload(payload_id=payload_id, tags_dumped_chunked=payload_dumped_chunked)

    logging.info(f"{kind} \t -- payload_id: {payload_id}, payload length: {len(payload)}")

    return {
        "kind": kind,
        "payloadId": payload_id,
        "payloadSize": len(payload_dumped_chunked)
    }


if __name__ == '__main__':
    handler({"payloadId": "123", "kind": "scrape-voting"}, None)
