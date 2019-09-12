"""
@author jacobi petrucciani
@desc qoo module
"""
import boto3
import os
from qoo.errors import FailedToCreateQueue
from qoo.queues import Job, Queue  # noqa
from typing import Any, List


AWS_DEFAULT_REGION = "us-east-1"


def _client(region: str = "") -> Any:
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
    """
    @cc 1
    @desc gets a qoo Queue object by SQS queue_name
    @arg queue_name: the name of the queue to return
    @ret a new qoo Queue object associated with the given queue
    """
    return Queue(queue_name, **kwargs)


def list_queues(region: str = "", verbose: bool = False) -> List[str]:
    """
    @cc 1
    @desc list all queues in the default or given region
    @arg region: the AWS region to list queues in
    @arg verbose: whether or not to return the fully qualified queue name
    @ret a list of queue names in the given region
    @note this will only list up to 1000 queue names!
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
    @cc 2
    @desc attempt to create an SQS queue and return it
    @arg queue_name: the name for this new queue
    @arg region: the AWS region to create in
    @arg delay_seconds: SQS message delay seconds
    @arg maximum_message_size: SQS max message size
    @arg message_retention_period: SQS message retention times
    @arg visibility_timeout: SQS message visibility timeout
    @arg fifo: whether to make a fifo queue or not
    @arg receive_message_wait_time_seconds: the amount of time to wait for a receive
    @note most of the common params are here, but you can pass additional_attributes if needed
    @ret a new qoo Queue object associated with the created queue
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
