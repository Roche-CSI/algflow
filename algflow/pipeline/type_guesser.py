from abc import ABC, abstractmethod
from typing import Any


# write an abstractlass which is the base class for guessing types of data given as Any
# the class should have a method called guess which takes `Any` and returns the guessed type
# the class should have a method called validate which takes a string and returns a boolean
# the class should have a method called convert which takes a string and returns the converted value
# the class should have a method called serialize which takes a value and returns a string

# abstract class DataTypeGuesser


# write a class which is a subclass of DataTypeGuesser and guesses string data

class DataTypeGuesser(ABC):
    @abstractmethod
    def guess(self, data: str) -> Any:
        pass

    @abstractmethod
    def validate(self, data: str) -> bool:
        pass

    @abstractmethod
    def convert(self, data: str) -> Any:
        pass

    @abstractmethod
    def serialize(self, data: Any) -> str:
        pass


class StringGuesser(DataTypeGuesser):
    def guess(self, data: str) -> Any:
        return str

    def validate(self, data: str) -> bool:
        return True

    def convert(self, data: str) -> Any:
        return data

    def serialize(self, data: Any) -> str:
        return str(data)
