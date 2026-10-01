import os
import boto3

SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]  # the dead-letter queue to drain


def main():
    session = boto3.Session()  # uses AWS_PROFILE

    sqs_client = session.client('sqs')
    lambda_client = session.client('lambda')


    while True:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5       
        )
        messages = response.get('Messages', [])

        if not messages:
            print("No messages found")
            break

        for message in messages:
            recipt_handle = message['ReceiptHandle']
            print(recipt_handle)

            payload = message['Body']
            print(payload)

            result = lambda_client.invoke(
                FunctionName="sejmoskop-prod-opensearch-ingest",
                InvocationType='RequestResponse',  # synchronizacja, czeka na wynik
                Payload=payload,
            )

            result_status_code = result['ResponseMetadata']['HTTPStatusCode']
            print(result_status_code)

            if result_status_code != 200:
                raise Exception("Error during lambda invocation")

            sqs_client.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=recipt_handle
            )


if __name__ == '__main__':
    main()
