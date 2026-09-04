import json
from errors.file_errors import FileError
from errors.parsing_errors import InvalidJsonFormat, InvalidSchema
from input.configuration import Configuration
from typing import Dict
from pydantic import TypeAdapter, ValidationError


class Parser:
    def __init__(self, config_file):
        self.config_file = config_file

    def open_config(self) -> Dict:
        try:
            with open(self.config_file, "r") as fd:
                data = json.load(fd)
            return data
        except FileNotFoundError:
            raise FileError("FileError exception occured."
                            f"{self.config_file} does not exist.")
        except json.JSONDecodeError:
            raise InvalidJsonFormat("InvalidJsonFormat exception occured."
                                    f"Make sure {self.config_file} contains"
                                    "valid JSON.")

    def parse_config(self) -> Configuration:
        input = self.open_config()
        try:
            config = TypeAdapter(Configuration).validate_python(input)
            return config
        except ValidationError:
            raise InvalidSchema("InvalidSchema exception occured.")
