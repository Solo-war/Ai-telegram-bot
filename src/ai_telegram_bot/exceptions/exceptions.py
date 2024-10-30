from dataclasses import dataclass

from .base import ApplicationBaseException


@dataclass(eq=False)
class CantGetFieldException(ApplicationBaseException):
    field_name: str

    @property
    def message(self):
        return f"Can't get field with name: {self.field_name}."


@dataclass(eq=False)
class RecognizeException(ApplicationBaseException):
    result: str

    @property
    def message(self):
        return f"When try to recognize happen exception. {self.result=}."
