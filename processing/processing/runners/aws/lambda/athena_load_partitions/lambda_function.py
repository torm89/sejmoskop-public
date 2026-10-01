import json
import logging

from processing.providers.aws import AwsProvider

logger = logging.getLogger()
logger.setLevel("INFO")


def handler(event, context):
    provider = AwsProvider()

    env_name = event['envName']
    table_names = json.loads(event['tableNames'])

    for table_name in table_names:
        provider.athena_run_query(
            QueryString=f"MSCK REPAIR TABLE `{table_name}`;",
            QueryExecutionContext={
                'Database': f"sejmoskop-{env_name}",
                'Catalog': "AwsDataCatalog"
            },
            WorkGroup=f"sejmoskop-{env_name}"
        )

    return {
        "env_name": env_name,
        "table_names": table_names
    }


if __name__ == "__main__":
    handler({"envName": 'dev'}, {})
