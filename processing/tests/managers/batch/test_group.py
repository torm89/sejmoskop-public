import os
from unittest.mock import patch


@patch.dict(os.environ, {"SJ_PROCESSING_GROUPS_TAGS_PER_JOB": "10"}, clear=True)
def test_tags_per_batch_job(batch_manager_group):
    assert batch_manager_group.tags_per_job() == 10


def test_payload_s3_key(batch_manager_group):
    assert batch_manager_group.payload_s3_key("1") == "processing/group/1.json"
