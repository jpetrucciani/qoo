"""
@author jacobi petrucciani
@desc qoo module
"""
import boto3
import os
from qoo.errors import FailedToCreateQueue
from qoo.queues import Job, Queue  # noqa
from typing import List


AWS_DEFAULT_REGION = "us-east-1"


def _client(region: str = ""):
    """
    @cc 1
    @desc generate a boto3 sqs client
    @arg region: the AWS region to connect to
    @ret a boto3 sqs client
    """
    region_name = region or os.environ.get("AWS_DEFAULT_REGION", AWS_DEFAULT_REGION)
    return boto3.client("sqs", region_name=region_name)


def login(
    access_key_id: str, secret_access_key: str, region: str = AWS_DEFAULT_REGION
) -> None:
    """
    @cc 1
    @desc sets environment variables for boto3.
    @arg access_key_id: AWS access key id
    @arg secret_access_key:  AWS secret access key
    @arg region: AWS region to login to
    """
    os.environ["AWS_ACCESS_KEY_ID"] = access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret_access_key
    os.environ["AWS_DEFAULT_REGION"] = region


def get(queue_name: str, **kwargs) -> Queue:
    """gets a qoo Queue object by SQS queue_name"""
    return Queue(queue_name, **kwargs)


def list_queues(region: str = "", verbose: bool = False) -> List[str]:
    """
    list all queues in the default or given region
    :note: this will only list up to 1000 queue names
    """
    sqs_client = _client(region=region)
    return [
        (x if verbose else x.split("/")[-1])
        for x in sqs_client.list_queues()["QueueUrls"]
    ]


def create(
    queue_name: str,
    region: str = "",
    delay_seconds: int = 0,
    maximum_message_size: int = 262144,
    message_retention_period: int = 345600,
    visibility_timeout: int = 30,
    fifo: bool = False,
    receive_message_wait_time_seconds: int = 0,
    **additional_attributes
) -> Queue:
    """
    attempt to create an SQS queue and return it
    :note: most of the common params are here, but you can pass additional_attributes if needed
    """
    sqs_client = _client(region=region)
    new_queue_url = sqs_client.create_queue(
        QueueName=queue_name,
        Attributes=dict(
            DelaySeconds=str(delay_seconds),
            MaximumMessageSize=str(maximum_message_size),
            MessageRetentionPeriod=str(message_retention_period),
            ReceiveMessageWaitTimeSeconds=str(receive_message_wait_time_seconds),
            VisibilityTimeout=str(visibility_timeout),
            FifoQueue=str(fifo).lower(),
            **additional_attributes
        ),
    )
    if not new_queue_url:
        raise FailedToCreateQueue()
    return get(new_queue_url["QueueUrl"].split("/")[-1])
