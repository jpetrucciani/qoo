"""
qoo pytest configuration
"""
import qoo
import os
import pytest
import time
from moto import mock_sqs
from typing import Generator


# this is to attempt to hack our way around boto issues
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(autouse=True)
def login() -> Generator:
    """fixture that will automatically set the login variables."""
    qoo.login("access_key", "secret_key")
    yield


@pytest.fixture
def queue() -> Generator:
    """fixture that provides an SQS qoo."""
    with mock_sqs():
        yield qoo.create("qoo")


@pytest.fixture
def fifo_queue() -> Generator:
    """fixture that provides a fifo SQS qoo."""
    with mock_sqs():
        yield qoo.create("qoo-fifo", fifo=True)


@pytest.fixture
def queue_with_job(queue: qoo.Queue) -> qoo.Queue:
    """fixture that provides a job"""
    queue.send_job(test="test message", sent_at=int(time.time()))
    return queue


@pytest.fixture
def queue_with_jobs(queue: qoo.Queue) -> qoo.Queue:
    """fixture that provides a queue and many jobs"""
    for x in range(10):
        queue.send_job(test="test message {}".format(x), sent_at=int(time.time()))
    return queue
