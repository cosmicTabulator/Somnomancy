class Impossible(Exception):
    """Exception raised when an action is impossible to perform

    The reason is given as the exception message
    """

class QuitWithoutSaving(SystemExit):
    """Can be raised to exit the game without automaticaly saving"""
