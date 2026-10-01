def copy_between_buckets(
        boto3_session, bucket_name_source, bucket_name_destination, path_prefix_source, path_prefix_destination,
        acl='private'
):
    client_s3 = boto3_session.client('s3')

    params = {
        "Bucket": bucket_name_source,
        "Prefix": path_prefix_source,
    }
    for _ in range(int(10e5)):
        response = client_s3.list_objects_v2(**params)

        for obj in response['Contents']:
            client_s3.copy_object(
                Bucket=bucket_name_destination,
                Key=f'{path_prefix_destination}/{obj["Key"]}',
                CopySource=f'{bucket_name_source}/{obj["Key"]}',
                ACL=acl
            )

        continuation_token = response.get('ContinuationToken', None)
        if continuation_token:
            params["ContinuationToken"] = continuation_token
        else:
            break
