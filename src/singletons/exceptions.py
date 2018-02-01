"""
Exceptions/Warnings
"""


class NoGreenthreadEnvironmentWarning(UserWarning):
    """
    Raised when a Greenthread scope is used but no greenthread environment is detected
    """
