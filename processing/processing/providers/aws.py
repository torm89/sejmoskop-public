import json
import os
import re
import tempfile
import time
from functools import cached_property
from pathlib import Path
from typing import Dict, List

import boto3
import requests
from aiobotocore.session import get_session
from opensearchpy import OpenSearch, RequestsHttpConnection
from sqlalchemy import create_engine, false


class AwsProvider:
    TAG_CLASS = None

    def __init__(self):
        self._athena_result_reuse_configuration_enabled = True
        self._athena_result_reuse_configuration_max_age = 3  # minutes

    @staticmethod
    def get_request_json(url: str):
        return requests.get(url).json()

    @property
    def aws_container_credentials_relative_uri(self) -> str:
        return f"http://169.254.170.2{os.environ['AWS_CONTAINER_CREDENTIALS_RELATIVE_URI']}"

    @property
    def aws_container_credentials(self) -> Dict:
        uri = self.aws_container_credentials_relative_uri
        response = self.get_request_json(url=uri)

        return {
            "aws_access_key_id": response['AccessKeyId'],
            "aws_secret_access_key": response['SecretAccessKey'],
            "aws_session_token": response['Token']
        }

    @property
    def aws_environment_credentials(self) -> Dict:
        return {
            "aws_access_key_id": os.environ['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": os.environ['AWS_SECRET_ACCESS_KEY'],
        }

    @property
    def aws_lambda_credentials(self) -> Dict:
        return {}

    @property
    def aws_credentials(self):
        if os.environ.get('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI'):
            return self.aws_container_credentials
        elif os.environ.get('LOCAL_ENVIRONMENT'):
            return self.aws_environment_credentials
        else:
            return self.aws_lambda_credentials

    @property
    def aws_region_name(self) -> str:
        return os.environ['AWS_REGION_NAME']

    @property
    def boto3_session(self):
        return boto3.Session(
            region_name=self.aws_region_name,
            **self.aws_credentials
        )

    @property
    def client_s3(self):
        return self.boto3_session.client('s3')

    def s3_list_objects(self, bucket_name: str, prefix: str) -> List[Dict]:
        paginator, objs = self.client_s3.get_paginator('list_objects_v2'), []
        for response in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            objs.extend(response.get('Contents', []))

        return objs

    def s3_get_object(self, bucket_name: str, key: str) -> str:
        response = self.client_s3.get_object(Bucket=bucket_name, Key=key)
        return response['Body'].read()

    def s3_download_object(self, bucket_name: str, key: str, path: str) -> None:
        with open(path, 'wb') as f:
            self.client_s3.download_fileobj(bucket_name, key, f)

    def s3_save_object(self, bucket_name: str, key: str, data: bytes, **kwargs) -> None:
        self.client_s3.put_object(Bucket=bucket_name, Key=key, Body=data, **kwargs)

    def s3_copy_object(self, bucket_name: str, key: str, source_path, acl='private') -> None:
        self.client_s3.copy_object(Bucket=bucket_name, Key=key, CopySource=source_path, ACL=acl)

    async def client_async(self, service_name: str):
        session = get_session()
        region_name = self.aws_region_name
        async with session.create_client(service_name, region_name=region_name, **self.aws_credentials) as client:
            yield client

    @property
    def client_s3_async(self):
        return self.client_async('s3')

    async def s3_save_objects_bulk(self, objs: List[Dict]):
        session = get_session()
        async with session.create_client(
                's3', region_name=self.aws_region_name, **self.aws_credentials
        ) as client_s3_async:
            for obj in objs:
                await client_s3_async.put_object(
                    Bucket=obj['bucket_name'],
                    Key=obj['key'],
                    Body=obj['data']
                )

    async def s3_get_object_async(self, bucket_name: str, key: str) -> str:
        session = get_session()
        async with session.create_client(
                's3', region_name=self.aws_region_name, **self.aws_credentials
        ) as client_s3_async:
            response = await client_s3_async.get_object(Bucket=bucket_name, Key=key)
            async with response['Body'] as stream:
                return await stream.read()

    @staticmethod
    def s3_get_object_bucket_and_key_from_url(url: str) -> dict:
        r = re.search(r'^s3://(?P<bucket_name>.+)/(?P<key>.+)$', url)
        return {"bucket_name": r.group('bucket_name'), "key": r.group('key')}

    def s3_get_object_from_url(self, url: str) -> str:
        return self.s3_get_object(**self.s3_get_object_bucket_and_key_from_url(url))

    def s3_download_object_from_url(self, url: str, path: str) -> None:
        self.s3_download_object(**self.s3_get_object_bucket_and_key_from_url(url), path=path)

    @property
    def client_athena(self):
        return self.boto3_session.client('athena')

    @property
    def athena_database_name(self):
        return os.environ['AWS_ATHENA_DATABASE_NAME']

    @property
    def athena_workgroup_name(self):
        return os.environ['AWS_ATHENA_WORKGROUP_NAME']

    @property
    def athena_result_reuse_configuration_enabled(self):
        return self._athena_result_reuse_configuration_enabled

    @athena_result_reuse_configuration_enabled.setter
    def athena_result_reuse_configuration_enabled(self, value):
        self._athena_result_reuse_configuration_enabled = value

    @property
    def athena_result_reuse_configuration_max_age(self):
        return self._athena_result_reuse_configuration_max_age

    @athena_result_reuse_configuration_max_age.setter
    def athena_result_reuse_configuration_max_age(self, value):
        self._athena_result_reuse_configuration_max_age = value

    def athena_run_query(self, directory_path: Path = None, **kwargs) -> Path:
        response = self.client_athena.start_query_execution(**kwargs)
        query_execution_id = response['QueryExecutionId']

        status = 'RUNNING'
        response = {}

        for _ in range(int(10e6)):
            response = self.client_athena.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']

            time.sleep(1)

            if status not in ["RUNNING", "QUEUED"]:
                break

        if status == "FAILED":
            reason = response['QueryExecution']['Status'].get('StateChangeReason', 'unknown reason')
            raise Exception(f'Query execution failed: {reason}')

        result_s3_location = response['QueryExecution']['ResultConfiguration']['OutputLocation']

        if directory_path is None:
            directory_path = Path(tempfile.mkdtemp())

        filepath = directory_path / query_execution_id
        self.s3_download_object_from_url(result_s3_location, filepath)

        return filepath

    @property
    def client_sf(self):
        return self.boto3_session.client('stepfunctions')

    def sf_send_task_success(self, task_token):
        self.client_sf.send_task_success(taskToken=task_token, output=json.dumps({})) if task_token else None

    def sf_send_task_failure(self, task_token):
        self.client_sf.send_task_failure(taskToken=task_token, error=json.dumps({})) if task_token else None

    @property
    def client_ssm(self):
        return self.boto3_session.client('ssm')

    def ssm_get_parameter(self, **kwargs):
        return self.client_ssm.get_parameter(**kwargs)

    @property
    def ssm_database_credentials_parameter_name(self):
        return os.environ['AWS_SSM_DATABASE_CREDENTIALS_PARAMETER_NAME']

    @cached_property
    def get_database_credentials(self):
        response = self.client_ssm.get_parameter(
            Name=self.ssm_database_credentials_parameter_name,
            WithDecryption=True,
        )
        return response['Parameter']['Value'].split(',')

    @property
    def ssm_opensearch_credentials_parameter_name(self):
        return os.environ['AWS_SSM_OPENSEARCH_CREDENTIALS_PARAMETER_NAME']

    @cached_property
    def get_opensearch_endpoint(self):
        response = self.client_ssm.get_parameter(
            Name=self.ssm_opensearch_credentials_parameter_name,
            WithDecryption=True,
        )
        return response['Parameter']['Value'].split(',')[2:]

    @cached_property
    def get_opensearch_credentials(self):
        response = self.client_ssm.get_parameter(
            Name=self.ssm_opensearch_credentials_parameter_name,
            WithDecryption=True,
        )
        return response['Parameter']['Value'].split(',')[:2]

    @property
    def athena_url(self):
        credentials = self.get_database_credentials
        aws_access_key_id, aws_secret_access_key = credentials[0], credentials[1]
        athena_database_name, athena_s3_bucket_name = credentials[2], credentials[3]

        return f"awsathena+rest://{aws_access_key_id}:{aws_secret_access_key}@athena.{self.aws_region_name}.amazonaws.com:443/{athena_database_name}?s3_staging_dir=s3://{athena_s3_bucket_name}/&result_reuse_enable={self.athena_result_reuse_configuration_enabled}&result_reuse_minutes={self.athena_result_reuse_configuration_max_age}"

    @property
    def athena_engine(self):
        return create_engine(self.athena_url)

    def client_opensearch(self) -> OpenSearch:
        [host, port] = self.get_opensearch_endpoint
        [username, password] = self.get_opensearch_credentials

        return OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=(username, password),
            http_compress=True,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            timeout=300
        )

    def client_cloudformation(self):
        return self.boto3_session.client('cloudformation')

    def cf_describe_stack(self, stack_name: str):
        return self.client_cloudformation().describe_stacks(StackName=stack_name)
