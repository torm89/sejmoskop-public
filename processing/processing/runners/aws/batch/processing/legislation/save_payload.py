import logging
from argparse import ArgumentParser

from processing.manager.outcomes import Manager
from processing.models.tags import TermTag, ScrapeMode

logging.basicConfig(level=logging.INFO)

from processing.utils.log_forwarding import attach_log_forwarding

# Must run after basicConfig: it no-ops when the root logger already has a handler,
# so attaching ours first would silently drop the CloudWatch stream.
attach_log_forwarding(logging.getLogger())


def main(payload_id: str, scrape_mode: ScrapeMode, term_tag: TermTag):
    manager = Manager()
    manager.save_processing_legislation_payload(payload_id=payload_id, scrape_mode=scrape_mode, term_tag=term_tag)


if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument('--payloadId', help='...')
    parser.add_argument('--scraperMode', help='...')
    parser.add_argument('--chamberName', help='...')
    parser.add_argument('--termId', help='...')

    args = parser.parse_args()

    main(
        payload_id=args.payloadId,
        scrape_mode=ScrapeMode(args.scraperMode),
        term_tag=TermTag(chamberName=args.chamberName, termId=args.termId)
    )
