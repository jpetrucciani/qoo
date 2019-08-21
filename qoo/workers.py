"""
worker class - not yet used
"""
from time import sleep


class Worker:
    """worker class"""

    def __init__(self, queues):
        """worker constructor"""
        self.queues = queues

    def __str__(self) -> str:
        """return a human-friendly object representation"""
        return "<Worker[{}]>".format(self.queues)

    def __repr__(self) -> str:
        """repr"""
        return self.__str__()

    def work(self, burst=False, wait_seconds=5):
        """work method"""
        while True:
            for queue in self.queues:
                for job in queue.jobs:
                    job.run()
                    queue.remove_job(job)

            if not burst:
                sleep(wait_seconds)
