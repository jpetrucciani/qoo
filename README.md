[![image](https://travis-ci.org/jpetrucciani/qoo.svg?branch=master)](https://travis-ci.org/jpetrucciani/qoo)
[![PyPI
version](https://badge.fury.io/py/qoo.svg)](https://badge.fury.io/py/qoo)
[![Code style:
black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Python 3.5+
supported](https://img.shields.io/badge/python-3.5+-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Documentation style:
archives](https://img.shields.io/badge/docstyle-archives-lightblue.svg)](https://github.com/jpetrucciani/archives)

**qoo** is a very simple Amazon SQS client, written in Python. It aims
to be much more straight-forward to use than boto3, and specializes only
in Amazon SQS, ignoring the rest of the AWS ecosystem.

# Features

- Easier interaction with SQS queues
- Automatic support for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
  and `AWS_DEFAULT_REGION` environment variables.
- automatic useful message/job metadata

# Usage

## Installation

```bash
pip install qoo
```

## Basic Usage

```python
import qoo

# list SQS queue names
qoo.list_queues()

# get an existing queue
queue = qoo.get("$QUEUE_NAME")

# or create a queue
queue = qoo.create("$QUEUE_NAME")

# send a job, pass info/keys as kwargs
queue.send(info="foo", user_id="test_user")  # etc.

# get an approximate count of messages in the queue
len(queue)                # approximate total messages
queue.approx_not_visible  # approximate number of message in the visibility timeout

# get a job
job = queue.receive(wait_time=1)
job.elapsed      # time between sending the job and receiving it
job.md5_matches  # boolean property to show that the md5 of the job matches what was sent

# and the data from the job is automatically converted into attrs
job.info         # the string "foo"
job.user_id      # the string "test_user"

# delete the job from the SQS queue
job.delete()
```

# Testing

Tests can be run with tox\!

```bash
# run tests
tox
```
