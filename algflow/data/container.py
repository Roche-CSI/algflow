from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal, Any

from algflow.data.dict_handler import DictHandler
from algflow.data.handler import AlgFlowDataHandler, DataHandlerManager


@dataclass
class DataContainer:
    """
    InputSource is a dataclass which represents a source of input for the algflow.
    The source represents a data file such as h5, parquet, csv, sql or event a database.
    The handler provides the handle to a plugin which can read the file
    and provides and describes the data.
    """
    type: Literal["input", "output", "param"]
    path: Optional[Path] = None  # in case of dict based data container, it could be null
    content_type: Optional[str] = None
    scope: Optional[str] = None
    handler: AlgFlowDataHandler = None

    def __post_init__(self):
        if not self.handler and self.path:
            handler_klass = DataHandlerManager().get_handler(self.path, self.content_type)
            self.handler = handler_klass(self.path, mode=self.type, scope=self.scope)



    @classmethod
    def create_dict_data_container(cls, type: str, data: dict[str, Any]):
        # handler_klass = DataHandlerManager().get_handler('dict', 'python/dict')
        return cls(type=type, handler=DictHandler(data))

    @classmethod
    def empty(cls, type: str):
        return cls(type=type, handler=DictHandler({}))
