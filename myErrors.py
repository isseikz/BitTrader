import numpy as np


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class SnapshotOrderError(Error):
    """Exception raised for the unexpected order of a snapshot

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message    = message


def checkSnapshotOrder(snapshots):
    s = snapshots.shape
    for i in range(0,s[0]):
        for j in range(0,s[1]-1):
            if (snapshots[i,j,0] < snapshots[i,j+1,0]):
                print(snapshots[i,:,0])
                print(i,snapshots[i,j,0], snapshots[i,j+1,0])
                expression = "Snapshot order error"
                message    = """
                Exception raised for the unexpected order of a snapshot.
                Please check the snapshots is below:
                    price
                      higher
                        ^
                        | ask
                        |
                     midPrice
                        |
                        | bid
                        |
                      lower

                """
                raise SnapshotOrderError(expression, message)


class InputErrors(Error):
    """Exception raised for the unexpected input

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message    = message

def shouldBeSingleInt(obj):
    # variable should be an integer
    if not isinstance(obj, int):
        expression = "shouldBeSingleInt error"
        message    = "shoule be an integer, not an list, float, datetime etc..."
        raise InputErrors(expression, message)
