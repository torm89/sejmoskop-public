import os
import json
import logging
import re

from processing.providers.aws import AwsProvider

logger = logging.getLogger()
logger.setLevel("INFO")


def handler(event, context):
    provider = AwsProvider()

    bucket_name = event['bucketName']

    terms = []
    paginator = provider.client_s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket_name, Prefix='web/terms'):
        for c in result.get('Contents', []):
            if c.get('Key').endswith('stamp.json'):
                response = provider.s3_get_object(bucket_name=bucket_name, key=c['Key'])

                terms.append(json.loads(response))

    provider.s3_save_object(
        bucket_name=bucket_name, key='web/sitemap/terms.json', data=json.dumps(terms, indent=2).encode('utf-8'))

    members = []
    paginator = provider.client_s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket_name, Prefix='web/members'):
        for c in result.get('Contents', []):
            key = c.get('Key')
            if key.endswith('members.json'):
                response = provider.s3_get_object(bucket_name=bucket_name, key=key)

                r = re.search(r'^web/members/(?P<chamberName>[\w-]+)/(?P<termId>\w+)/members\.json$', key)

                records = json.loads(response)
                records = map(
                    lambda re: {"chamber_name": r.group('chamberName'), "term_id": r.group('termId'), **re}, records)

                members.extend(records)

    provider.s3_save_object(
        bucket_name=bucket_name, key='web/sitemap/members.json', data=json.dumps(members, indent=2).encode('utf-8'))

    legislation = []
    paginator = provider.client_s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket_name, Prefix='web/legislation'):
        for c in result.get('Contents', []):
            key = c.get('Key')

            # Match only the per-term list (web/legislation/{chamber}/{term}/legislation.json),
            # not the per-process detail at .../{number}/legislation.json (same file name, one level deeper).
            r = re.search(r'^web/legislation/(?P<chamberName>[\w-]+)/(?P<termId>\w+)/legislation\.json$', key)
            if not r:
                continue

            response = provider.s3_get_object(bucket_name=bucket_name, key=key)

            records = json.loads(response)
            records = map(
                lambda record: {"chamber_name": r.group('chamberName'), "term_id": r.group('termId'), **record},
                records)

            legislation.extend(records)

    provider.s3_save_object(
        bucket_name=bucket_name, key='web/sitemap/legislation.json',
        data=json.dumps(legislation, indent=2).encode('utf-8'))

    return {
        "bucket_name": bucket_name,
    }


if __name__ == "__main__":
    handler({"bucketName": os.environ['AWS_S3_DATA_BUCKET_NAME']}, {})
