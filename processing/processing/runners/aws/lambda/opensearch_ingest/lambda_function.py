import os
import json
import logging
import urllib.parse

from processing.models.data.os import statement
from processing.providers.aws import AwsProvider
from processing.utils.utils import chunks

logger = logging.getLogger()
logger.setLevel("INFO")


def handler(event, context):
    provider = AwsProvider()

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    obj = provider.s3_get_object(bucket, key)
    directory = key.split('/')[1]

    if directory == 'statements':
        payload = statement.prepare_bulk_payload(json.loads(obj))
    else:
        raise ValueError(f"Unhandled index ingest: {directory}")

    opensearch_client = provider.client_opensearch()

    for chunk in chunks(payload, 30):  # n cannot be odd
        response = opensearch_client.bulk("\n".join(chunk))

        if response['errors']:
            logger.error(response)
            raise Exception("Error during bulk ingest")

    return 0


if __name__ == "__main__":
    provider = AwsProvider()

    bucket_name = os.environ['AWS_S3_DATA_BUCKET_NAME']
    for obj in provider.s3_list_objects(bucket_name, 'opensearch/statements/senat'):
        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": bucket_name
                        },
                        "object": {
                            "key": obj['Key']
                        }
                    }
                }
            ]
        }
        print(obj['Key'])
        handler(event, None)
