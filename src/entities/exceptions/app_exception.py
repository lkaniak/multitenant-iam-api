from typing import Optional


class AppException(Exception):

    error_code: str
    status_code: Optional[int]
    details: Optional[str]
    internal: Optional[str]
    quiet: bool

    def __init__(
        self,
        error_code: str,
        quiet=True,
        status_code: Optional[int] = 500,
        details: Optional[str] = None,
        internal: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.error_code = error_code
        self.quiet = quiet
        self.status_code = status_code
        self.details = details
        self.internal = internal
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        if self.quiet:
            return "An error has occurred."
        return super().__str__()
