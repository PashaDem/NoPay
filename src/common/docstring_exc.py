class DocStringException(Exception):
    """Base class for exception based on docstring message."""

    def __init__(self, msg: str | None = None) -> None:
        """Contain logic of using docstring if msg isn't provided."""
        super().__init__(msg or self.__doc__)
