from entities.exceptions.app_exception import AppException


class MultipleExceptions(Exception):

    exceptions: list[AppException]

    def __init__(self, exceptions: list[AppException]):
        self.exceptions = exceptions

    def __str__(self):
        errors = [str(exception) for exception in self.exceptions]
        error_str = "\n".join(errors)
        return f"Multiple errors occurred: {error_str}"

    @classmethod
    def handle_multiple_exceptions(cls, exceptions: list[AppException]):
        if len(exceptions) == 1:
            return exceptions[0]
        elif len(exceptions) > 1:
            return MultipleExceptions(exceptions=exceptions)
        return None
