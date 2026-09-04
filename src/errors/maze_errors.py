class MazeGenerationError(Exception):
    def __init__(self,
                 message: str = "MazeGenerationError exception"
                 "occured.") -> None:
        self.message = message
        super().__init__(self.message)
