import asyncio
import logging
from argparse import ArgumentParser

from aiobotocore.session import get_session

from processing.providers.aws import AwsProvider

logging.basicConfig(level=logging.INFO)

from processing.utils.log_forwarding import attach_log_forwarding

# Must run after basicConfig: it no-ops when the root logger already has a handler,
# so attaching ours first would silently drop the CloudWatch stream.
attach_log_forwarding(logging.getLogger())


async def copy(source_bucket_name, source_prefix, destination_bucket_name, acl):
    provider = AwsProvider()

    session = get_session()
    async with session.create_client(
            's3', region_name=provider.aws_region_name, **provider.aws_credentials
    ) as client_s3:

        paginator = client_s3.get_paginator('list_objects_v2')
        async for result in paginator.paginate(Bucket=source_bucket_name, Prefix=source_prefix):

            for c in result.get('Contents', []):
                response = await client_s3.get_object(Bucket=source_bucket_name, Key=c['Key'])

                async with response['Body'] as stream:
                    data = await stream.read()

                    await client_s3.put_object(
                        Bucket=destination_bucket_name,
                        Key=c['Key'],
                        Body=data,
                        ACL=acl
                    )


def main(source_bucket_name, source_prefix, destination_bucket_name, acl):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        copy(
            source_bucket_name=source_bucket_name,
            source_prefix=source_prefix,
            destination_bucket_name=destination_bucket_name,
            acl=acl
        )
    )

    return {
        "acl": acl,
        "source_prefix": source_prefix,
        "source_bucket_name": source_bucket_name,
        "destination_bucket_name": destination_bucket_name,
    }


if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument('--sourceBucketName', help='...')
    parser.add_argument('--sourcePrefix', help='...')
    parser.add_argument('--destinationBucketName', help='...')
    parser.add_argument('--acl', help='...')

    args = parser.parse_args()

    main(
        source_bucket_name=args.sourceBucketName,
        source_prefix=args.sourcePrefix,
        destination_bucket_name=args.destinationBucketName,
        acl=args.acl
    )
