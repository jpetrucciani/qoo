"""
@author jacobi petrucciani
@desc custom qoo errors
"""


class QooException(Exception):
    """
    @desc base qoo exception class
    """

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        """
        @cc 2
        @desc QooException constructor
        """
        extra = ""
        if args:
            extra = '\n| extra info: "{extra}"'.format(extra=args[0])
        print(
            "[{exception}]: {doc}{extra}".format(
                exception=self.__class__.__name__, doc=self.__doc__, extra=extra
            )
        )
        Exception.__init__(self, *args)


class InvalidCredentials(QooException):
    """
    @desc invalid credentials were passed for a queue object
    """


class FailedToCreateQueue(QooException):
    """
    @desc attempting to create a queue has failed
    """
