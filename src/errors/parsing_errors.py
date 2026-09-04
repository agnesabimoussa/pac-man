class InvalidJsonFormat(Exception):
    def __init__(self,
                 message: str = "InvalidJsonFormat exception"
                 "occured.") -> None:
        self.message = message
        super().__init__(self.message)


class InvalidSchema(Exception):
    def __init__(self,
                 message: str = "InvalidSchema exception"
                 "occured.") -> None:
        self.message = message
        super().__init__(self.message)
