"""
pytest the qoo functionality
"""
import os
import qoo
import pytest
import time
from moto import mock_sqs


def test_login():
    """
    Ensure that login sets the correct environment variables.

    The ``login`` fixture sets these automatically.
    """
    assert os.environ["AWS_ACCESS_KEY_ID"] == "access_key"
    assert os.environ["AWS_SECRET_ACCESS_KEY"] == "secret_key"
    assert os.environ["AWS_DEFAULT_REGION"] == "us-east-1"


@mock_sqs
def test_queues_can_be_created():
    """test that we can create a queue"""
    queue = qoo.create("test_queue")
    assert queue.name == "test_queue"
    assert queue.created_at < time.time()
    assert queue.maximum_message_size == 262144
    assert not queue.fifo


@mock_sqs
def test_fifo_queues_can_be_created():
    """test that we can create a queue"""
    queue = qoo.create("test_queue", fifo=True)
    assert queue.name == "test_queue"
    assert queue.created_at < time.time()
    assert queue.maximum_message_size == 262144
    assert queue.fifo


@mock_sqs
def test_queues_are_not_auto_created():
    """tests that we are not creating queues on init"""
    sqs = qoo._client()
    with pytest.raises(sqs.exceptions.QueueDoesNotExist):
        qoo.get("this_isnt_a_queue")


def test_can_send_job(queue):
    """test that we can send a job into the queue"""
    queue.send(info="test_job")
    assert len(queue) > 0


def test_can_send_and_receive_job(queue):
    """test that we can send a job into the queue, and pull it back out"""
    queue.send(info="test_job")
    assert len(queue) > 0
    job = queue.receive()
    assert job
    assert job.md5_matches


def test_can_delete_job(queue_with_job):
    """test that we can delete a job from the queue"""
    job = queue_with_job.receive()
    del job
    next_job = queue_with_job.receive(wait_time=1)
    assert not next_job


def test_pull_two_jobs(queue_with_jobs):
    """test that we can pull 2 jobs in one call"""
    assert len(queue_with_jobs) == 10
    job_0 = queue_with_jobs.receive()
    job_1 = queue_with_jobs.receive()
    assert job_0.test
    assert job_1.test
    assert job_0.test == "test message 0"
    assert job_1.test == "test message 1"
