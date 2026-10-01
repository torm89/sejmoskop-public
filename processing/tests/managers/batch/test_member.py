import os
from unittest.mock import patch


@patch.dict(os.environ, {"SJ_PROCESSING_MEMBERS_TAGS_PER_JOB": "10"}, clear=True)
def test_tags_per_batch_job(batch_manager_member):
    assert batch_manager_member.tags_per_job() == 10


def test_payload_s3_key(batch_manager_member):
    assert batch_manager_member.payload_s3_key("1") == "processing/member/1.json"
