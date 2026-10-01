import logging

from processing.providers.aws import AwsProvider

logger = logging.getLogger()
logger.setLevel("INFO")


class StackOperationInProgress(Exception):
    pass


class StackOperationFailed(Exception):
    pass


def handler(event, context):
    provider = AwsProvider()

    stack_name = event['stack_name']

    response = provider.cf_describe_stack(stack_name)
    stack_status = response['Stacks'][0]['StackStatus']

    if stack_status.endswith("IN_PROGRESS"):
        raise StackOperationInProgress(f"Stack {stack_name} is in progress")
    elif stack_status.endswith("FAILED") or stack_name == "ROLLBACK_COMPLETE":
        raise StackOperationFailed(f"Stack {stack_name} failed")

    return {
        output['OutputKey']: output['OutputValue']
        for output in response['Stacks'][0]['Outputs']
    }


if __name__ == "__main__":
    handler({"envName": 'dev'}, {})
