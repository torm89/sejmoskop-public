import datetime
import json


def create_update_stamp(boto3_session, bucket_name, stamp_key):
    client_s3 = boto3_session.client('s3')

    content = json.dumps(datetime.datetime.now().isoformat(), indent=2)
    client_s3.put_object(Body=content.encode(), Bucket=bucket_name, Key=stamp_key)
