"""
@author jacobi petrucciani
@desc pytest the qoo functionality
"""
import json
import os
import pytest
import qoo
import sys
import time
from moto import mock_sqs


def dbg(text) -> None:
    """debug printer for tests"""
    if isinstance(text, dict):
        text = json.dumps(text, sort_keys=True, indent=2)
    caller = sys._getframe(1)
    print("")
    print("----- {} line {} ------".format(caller.f_code.co_name, caller.f_lineno))
    print(text)
    print("-----")
    print("")


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
    queue = qoo.create("test_queue.fifo", fifo=True)
    assert queue.name == "test_queue.fifo"
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


def test_can_send_batch_jobs(queue):
    """test that we can send many jobs into the queue"""
    responses = queue.send_batch(
        [
            {"job": 0, "message": "test 0"},
            {"job": 1, "message": "test 1"},
            {"job": 2, "message": "test 2"},
            {"job": 3, "message": "test 3"},
            {"job": 4, "message": "test 4"},
            {"job": 5, "message": "test 5"},
            {"job": 6, "message": "test 6"},
            {"job": 7, "message": "test 7"},
            {"job": 8, "message": "test 8"},
            {"job": 9, "message": "test 9"},
            {"job": 10, "message": "test 10"},
            {"job": 11, "message": "test 11"},
            {"job": 12, "message": "test 12"},
            {"job": 13, "message": "test 13"},
            {"job": 14, "message": "test 14"},
            {"job": 15, "message": "test 15"},
            {"job": 16, "message": "test 16"},
            {"job": 17, "message": "test 17"},
            {"job": 18, "message": "test 18"},
            {"job": 19, "message": "test 19"},
            {"job": 20, "message": "test 20"},
        ]
    )
    assert len(queue) == 21
    assert len(responses["Successful"]) == 21

    # send as list of strings
    responses = queue.send_batch(
        [
            "this",
            "is",
            "an",
            "example",
            "of",
            "sending",
            "batch",
            "messages",
            "as",
            "a",
            "list",
            "of",
            "strings",
        ]
    )
    assert len(queue) == 34
    assert len(responses["Successful"]) == 13
    jobs = queue.receive_jobs(max_messages=10)
    assert len(jobs) == 10
    assert "message" in jobs[0]
    assert jobs[0].job == 0
    jobs = queue.receive_jobs(max_messages=10)
    assert len(jobs) == 10
    jobs = queue.receive_jobs(max_messages=10)
    assert len(jobs) == 10
    jobs = queue.receive_jobs(max_messages=10)
    assert len(jobs) == 4


def test_can_send_and_receive_job(queue):
    """test that we can send a job into the queue, and pull it back out"""
    queue.send(info="test_job")
    assert len(queue) > 0
    job = queue.receive()
    assert job
    assert job.md5_matches
    assert job.approximate_receive_count == 1
    assert job.elapsed > 0.0


def test_can_purge_queue(queue_with_job):
    """test that we can purge a queue"""
    queue_with_job.purge()
    assert len(queue_with_job) == 0


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
