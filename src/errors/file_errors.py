class InvalidProgramArguments(Exception):
    def __init__(self,
                 message: str = "InvalidProgramArguments"
                 "exception occured.") -> None:
        self.message = message
        super().__init__(self.message)


class FileError(Exception):
    def __init__(self,
                 message: str = "FileError"
                 "exception occured.") -> None:
        self.message = message
        super().__init__(self.message)
