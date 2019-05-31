"""
queue class
"""
import boto3
import os
import time
import hashlib
from qoo.utils import jsond, jsonl


class Job(object):
    """a single unit of work"""

    def __init__(self, sqs_message: dict) -> None:
        """job constructor"""
        self._data = sqs_message
        self._md5 = self._data["MD5OfBody"]
        self._id = self._data["MessageId"]
        self._body = jsonl(self._data["Body"])
        self._received_at = int(time.time())
        for key in self._body:
            setattr(self, key, self._body[key])
        self.handle = self._data["ReceiptHandle"]

    def __str__(self) -> str:
        """return a human-friendly object representation"""
        return "<Job[{}]>".format(self._id)

    def __repr__(self) -> str:
        """repr"""
        return self.__str__()

    @property
    def md5_matches(self) -> bool:
        """verify contents of the message"""
        checksum = hashlib.md5(self._data["Body"].encode()).hexdigest()
        return self._md5 == checksum


class Queue(object):
    """sqs queue"""

    def __init__(
        self,
        name: str,
        region_name: str = "",
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
        max_messages: int = 1,
        wait_time: int = 10,
    ) -> None:
        """queue constructor"""
        self.name = name
        self._max_messages = max_messages
        self._wait_time = wait_time
        self._region_name = region_name or os.environ.get("AWS_DEFAULT_REGION")
        self._aws_access_key_id = aws_access_key_id or os.environ.get(
            "AWS_ACCESS_KEY_ID"
        )
        self._aws_secret_access_key = aws_secret_access_key or os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )

        client_args = {}
        if self._aws_access_key_id:
            client_args["aws_access_key_id"] = self._aws_access_key_id
        if self._aws_secret_access_key:
            client_args["aws_secret_access_key"] = self._aws_secret_access_key
        if self._region_name:
            client_args["region_name"] = self._region_name

        self._client = boto3.client("sqs", **client_args)
        self._region_name = self._client._client_config.region_name
        self._queue_url = self._client.get_queue_url(QueueName=self.name)["QueueUrl"]
        self._update_attributes()

    def __str__(self) -> str:
        """return a human-friendly object representation."""
        return "<Queue[{}] {}>".format(self._region_name, self.name)

    def __repr__(self) -> str:
        """repr"""
        return self.__str__()

    def _update_attributes(self) -> None:
        """pull the latest attributes and parse them into class attributes"""
        self._attributes = self._client.get_queue_attributes(
            QueueUrl=self._queue_url, AttributeNames=["All"]
        )["Attributes"]
        self.arn = self._attributes["QueueArn"]
        self.created_at = int(self._attributes["CreatedTimestamp"])
        self.updated_at = int(self._attributes["LastModifiedTimestamp"])
        self.visibility_timeout = int(self._attributes["VisibilityTimeout"])
        self.delay_seconds = int(self._attributes["DelaySeconds"])
        self.maximum_message_size = int(self._attributes["MaximumMessageSize"])
        self.message_retention_period = int(self._attributes["MessageRetentionPeriod"])
        self.receive_message_wait_time_seconds = int(
            self._attributes["ReceiveMessageWaitTimeSeconds"]
        )
        self.approx_messages = int(self._attributes["ApproximateNumberOfMessages"])
        self.approx_not_visible = int(
            self._attributes["ApproximateNumberOfMessagesNotVisible"]
        )
        self.approx_delayed = int(
            self._attributes["ApproximateNumberOfMessagesDelayed"]
        )

    def send_job(self, **attributes) -> str:
        """using the kwarg attributes, send a job to this queue."""
        attributes.update({"created_at": int(time.time())})
        response = self._client.send_message(
            MessageBody=jsond(attributes), QueueUrl=self._queue_url
        )
        return response["MessageId"]

    def receive_jobs(self) -> list:
        """receive a list of jobs from the queue"""
        jobs = self._client.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=self._max_messages,
            WaitTimeSeconds=self._wait_time,
        )
        if "Messages" not in jobs:
            return []
        return [Job(x) for x in jobs["Messages"]]

    def delete_job(self, handle: str) -> None:
        """delete a job"""
        self._client.delete_message(QueueUrl=self._queue_url, ReceiptHandle=handle)
