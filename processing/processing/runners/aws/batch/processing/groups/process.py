import logging
from argparse import ArgumentParser

from processing.manager.outcomes import Manager

logging.basicConfig(level=logging.INFO)

from processing.utils.log_forwarding import attach_log_forwarding

# Must run after basicConfig: it no-ops when the root logger already has a handler,
# so attaching ours first would silently drop the CloudWatch stream.
attach_log_forwarding(logging.getLogger())


def main(payload_id: str) -> None:
    manager = Manager()

    manager.process_processing_group_jobs(payload_id=payload_id)


if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument('--payloadId', help='...')

    args = parser.parse_args()

    main(payload_id=args.payloadId)
