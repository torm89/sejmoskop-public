import json
import logging
from datetime import datetime

from processing.providers.aws import AwsProvider

logger = logging.getLogger()
logger.setLevel("INFO")


def handler(event, context):
    provider = AwsProvider()

    key = event['key']
    bucket_name = event['bucketName']
    content = event['content']
    add_time_stamp = event['addTimeStamp'] == 'yes'

    if add_time_stamp:
        content = json.dumps({
            "time_stamp": datetime.utcnow().isoformat(),
            **json.loads(content)
        })

    provider.s3_save_object(
        bucket_name=bucket_name,
        key=key,
        data=content.encode('utf-8'),
    )

    return {
        "bucket_name": bucket_name,
        "content": content,
        "key": key,
    }


if __name__ == "__main__":
    handler({}, {})
