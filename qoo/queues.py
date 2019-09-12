"""
@author jacobi petrucciani
@desc qoo queue and job class
"""
import boto3
import os
import time
import hashlib
import json
from qoo.utils import chunk, jsond, jsonl, new_uuid
from typing import Dict, List, Optional, Union


MAX_MESSAGES = 10


class Job:
    """
    @desc a single unit of work
    """

    def __init__(self, sqs_message: dict, queue: "Queue") -> None:
        """
        @cc 2
        @desc job constructor
        @arg sqs_message: the dictionary of values to pass as a message
        @arg queue: the queue this message will be sent in
        """
        self._queue = queue
        self._data = sqs_message
        self._md5 = self._data["MD5OfBody"]
        self._id = self._data["MessageId"]
        try:
            self._body = jsonl(self._data["Body"])
            for key in self._body:
                setattr(self, key, self._body[key])
        except json.decoder.JSONDecodeError:
            self._body = self._data["Body"]
        self._attributes = self._data["Attributes"]
        self._sent_at = float(self._attributes["SentTimestamp"]) / 1000
        self._received_at = float(time.time())
        self.elapsed = self._received_at - self._sent_at
        self.approximate_receive_count = int(
            self._attributes["ApproximateReceiveCount"]
        )
        self._handle = self._data["ReceiptHandle"]

    def __contains__(self, key: str) -> bool:
        """
        @cc 1
        @desc check if the given key exists in this job
        @arg key: a key to check for in this job's attributes
        @ret true if the job contains this key
        """
        return key in dir(self)

    def __eq__(self, other: object) -> bool:
        """
        @cc 1
        @desc check if this Job is equal to another
        @arg other: another Job object to compare to
        @ret true if the jobs match
        """
        return isinstance(other, Job) and self._handle == other._handle

    def __str__(self) -> str:
        """
        @cc 1
        @desc return a human-friendly object representation
        @ret a string version of this job
        """
        return "<Job[{}]>".format(self._id)

    def __repr__(self) -> str:
        """
        @cc 1
        @desc return a human-friendly object representation in the repl
        @ret a repr version of this job
        """
        return self.__str__()

    def delete(self) -> Dict:
        """
        @cc 1
        @desc delete this object
        @ret the AWS response for deleting this message
        """
        return self._queue.delete_job(self._handle)

    @property
    def md5_matches(self) -> bool:
        """
        @cc 1
        @desc verify contents of the message
        @ret if this message's md5 matches the body of the message
        """
        checksum = hashlib.md5(self._data["Body"].encode()).hexdigest()
        return self._md5 == checksum


class Queue:
    """
    @desc sqs queue
    """

    SUCCESS = "Successful"
    FAILED = "Failed"

    def __init__(
        self,
        name: str,
        region_name: str = "",
        aws_access_key_id: str = "",
        aws_secret_access_key: str = "",
        max_messages: int = 1,
        wait_time: int = 10,
        async_send: bool = False,
    ) -> None:
        """
        @cc 4
        @desc queue constructor
        @arg name: the SQS queue's name
        @arg region_name: the region of the SQS queue
        @arg aws_access_key_id: your AWS access key id
        @arg aws_secret_access_key: your AWS secret access key
        @arg max_messages: the max messages to pull at each time
        @arg wait_time: the default wait time for receives
        @arg async_send: whether or not to send async TODO
        """
        self.name = name
        self._max_messages = max_messages
        self._wait_time = wait_time
        self._async = async_send
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
        """
        @cc 1
        @desc return a human-friendly object representation
        @ret a string version of this job
        """
        return "<Queue[{}] {}>".format(self._region_name, self.name)

    def __repr__(self) -> str:
        """
        @cc 1
        @desc return a human-friendly object representation in the repl
        @ret a repr version of this job
        """
        return self.__str__()

    def __len__(self) -> int:
        """
        @cc 1
        @desc attempt to get how many messages are in the queue
        @ret the number of messages in the queue
        @note this is an approximate only
        """
        self._update_attributes()
        return self.approx_messages

    def _update_attributes(self) -> None:
        """
        @cc 1
        @desc pull the latest attributes and parse them into class attributes
        """
        self._attributes = self._client.get_queue_attributes(
            QueueUrl=self._queue_url, AttributeNames=["All"]
        )["Attributes"]
        self.arn = self._attributes["QueueArn"]
        self.created_at = float(self._attributes["CreatedTimestamp"])
        self.updated_at = float(self._attributes["LastModifiedTimestamp"])
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
        self.fifo = "FifoQueue" in self._attributes

    def send(self, **attributes) -> str:
        """
        @cc 1
        @desc shorthand for send_job
        @ret the AWS response for sending this job
        """
        return self.send_job(**attributes)

    def send_job(self, **attributes) -> str:
        """
        @cc 1
        @desc using the kwarg attributes, send a job to this queue.
        @ret the AWS response for sending this job
        pass job attributes to set the message/job body
        """
        response = self._client.send_message(
            MessageBody=jsond(attributes), QueueUrl=self._queue_url
        )
        return response["MessageId"]

    def send_batch(
        self,
        raw_jobs: List[Union[Dict, str]],
        delay_seconds: int = 0,
        auto_metadata: bool = True,
    ) -> Dict:
        """
        @cc 3
        @desc send a batch of jobs to the queue, chunked into 10s
        @arg raw_jobs: a list of dicts or json encoded strings
        @arg delay_seconds: a number of seconds to delay sending
        @arg auto_metadata: whether or not to auto-add required metadata to each job
        @ret the AWS response for sending these jobs
        """
        jobs = raw_jobs
        successful = []  # type: List
        failed = []  # type: List

        # if default, treat each list item as just the message body
        if auto_metadata:
            jobs = [
                {
                    "Id": new_uuid(),
                    "MessageBody": x if isinstance(x, str) else jsond(x),
                    "DelaySeconds": delay_seconds,
                }
                for x in raw_jobs
            ]

        # send in batches of 10
        for job_batch in chunk(jobs, size=MAX_MESSAGES):
            response = self._client.send_message_batch(
                QueueUrl=self._queue_url, Entries=job_batch
            )
            if Queue.SUCCESS in response:
                successful.extend(response[Queue.SUCCESS])
            if Queue.FAILED in response:
                failed.extend(response[Queue.FAILED])

        # return the list of successful and failed jobs
        return {Queue.SUCCESS: successful, Queue.FAILED: failed}

    def receive_jobs(
        self,
        max_messages: int = None,
        wait_time: int = None,
        attribute_names: str = "All",
    ) -> List[Job]:
        """
        @cc 2
        @desc receive a list of jobs up to max_messages
        @arg max_messages: the limit to the number of messages to pull
        @arg wait_time: the amount of time to wait before returning
        @arg attribute_names: the attributes to return for each job, default All
        @ret a list of jobs from the queue
        @note this can return with an empty list!
        """
        num_messages = max_messages if max_messages else self._max_messages
        jobs = self._client.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=num_messages,
            WaitTimeSeconds=wait_time if wait_time else self._wait_time,
            AttributeNames=[attribute_names],
        )
        if "Messages" not in jobs:
            return []
        return [Job(x, self) for x in jobs["Messages"]]

    def receive(self, wait_time: int = None) -> Optional[Job]:
        """
        @cc 1
        @desc receive a single job from the queue
        @arg wait_time: the amount of time to wait before returning
        @ret none or a job
        """
        jobs = self.receive_jobs(max_messages=1, wait_time=wait_time)
        return jobs[0] if jobs else None

    def delete_job(self, handle: str) -> Dict:
        """
        @cc 1
        @desc delete a job by the message handle
        @arg handle: the message handle to delete
        @ret the AWS response for deleting this job
        """
        return self._client.delete_message(
            QueueUrl=self._queue_url, ReceiptHandle=handle
        )

    def purge(self) -> None:
        """
        @cc 1
        @desc purge the queue
        @warn this will delete all messages in the queue, and cannot be undone!
        """
        self._client.purge_queue(QueueUrl=self._queue_url)
