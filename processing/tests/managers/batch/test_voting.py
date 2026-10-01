import os
from unittest.mock import patch


@patch.dict(os.environ, {"SJ_PROCESSING_VOTINGS_TAGS_PER_JOB": "120"}, clear=True)
def test_tags_per_batch_job(batch_manager_voting):
    assert batch_manager_voting.tags_per_job() == 120


def test_payload_s3_key(batch_manager_voting):
    assert batch_manager_voting.payload_s3_key("11") == "processing/voting/11.json"
