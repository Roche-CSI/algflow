from dataclasses import dataclass, field
import time


@dataclass
class AlgflowEvent:
    name: str
    algorithm: str
    data: dict
    timestamp: int = field(default_factory=time.time)

    def __str__(self):
        return f'Event[{self.name}] {self.timestamp} {self.algorithm} {self.data}'


class ExecutionStartEvent(AlgflowEvent):
    def __init__(self, algorithm: str, data: dict):
        super().__init__('ExecutionStart', algorithm, data)

class ExecutionEndEvent(AlgflowEvent):
    def __init__(self, algorithm: str, data: dict):
        super().__init__('ExecutionEnd', algorithm, data)

class ExecutionErrorEvent(AlgflowEvent):
    def __init__(self, algorithm: str, debug_info: dict):
        super().__init__('ExecutionError', algorithm, debug_info)