import asyncio
import logging
import os
from argparse import ArgumentParser

from processing.manager.outcomes import Manager

logging.basicConfig(level=logging.INFO)

from processing.utils.log_forwarding import attach_log_forwarding

# Must run after basicConfig: it no-ops when the root logger already has a handler,
# so attaching ours first would silently drop the CloudWatch stream.
attach_log_forwarding(logging.getLogger())

if os.system == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main(payload_id: str) -> None:
    manager = Manager()

    manager.process_processing_statement_jobs(payload_id=payload_id)


if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument('--payloadId', help='...')
    parser.add_argument('--concraftPl2ServiceUrl', help='...')
    parser.add_argument('--concraftPl2ServicePort', help='...')

    args = parser.parse_args()

    os.environ['CONCRAFT_SERVER_ADDR'] = args.concraftPl2ServiceUrl
    os.environ['CONCRAFT_PORT'] = args.concraftPl2ServicePort

    main(payload_id=args.payloadId)
