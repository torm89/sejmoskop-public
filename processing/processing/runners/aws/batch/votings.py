import logging
import os
import sys
from argparse import ArgumentParser

# This script lives in runners/aws/batch/, which also holds a `processing/`
# subpackage. When run directly, Python puts this dir on sys.path[0] and that
# subpackage would shadow the top-level `processing` package, so drop it first.
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

from processing.manager.outcomes import Manager
from processing.models.tags import TermTag

logging.basicConfig(level=logging.INFO)

from processing.utils.log_forwarding import attach_log_forwarding

# Must run after basicConfig: it no-ops when the root logger already has a handler,
# so attaching ours first would silently drop the CloudWatch stream.
attach_log_forwarding(logging.getLogger())


def main(term_tag: TermTag) -> None:
    manager = Manager()
    manager.process_votings(term_tag=term_tag)


if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument('--chamberName', help='...')
    parser.add_argument('--termId', help='...')

    args = parser.parse_args()

    main(
        term_tag=TermTag(chamberName=args.chamberName, termId=args.termId)
    )
