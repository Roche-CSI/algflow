import re
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import List, Dict, Type, Any, Generator, Union, NewType, Optional
from importlib.metadata import entry_points

from algflow.common import Singleton
from algflow.data.spec import AlgFlowDataDescriptor

logger = logging.getLogger('Data Handler')
DataElements = NewType('Elements', Union[Generator[AlgFlowDataDescriptor, None, None], List[AlgFlowDataDescriptor]])


@dataclass
class PathSpec:
    """
    Input handlers will be searched by the extension first.
    If multiple handlers are found for the same extension,
    the filename will be matched against the pattern.
    If the filename pattern returns multiple handlers,
    then content_type will be used to resolve the conflict.
    Finally, InputHandlerConflict will be raised if more than one handler are found.
    """
    extension: str
    name_pattern: str = '^.*$'
    content_type: str = "text/plain"

    @cached_property
    def pattern_re(self):
        return re.compile(self.name_pattern)

    def match(self, path: str):
        return self.pattern_re.match(path) is not None


class AlgFlowDataHandler(ABC):
    """
        The input handler abstracts away the file format from rest of the AlgFlow system and exposes a key
        value database to the algflow. This abstraction allows algflow to consume io from `h5', 'parquet`, 'csv`,
        'sql' or any other file format or databases.

        Methods
        -------
        pathspec -> PathSpec
            This is a class method which must be defined by the handler.
            The method returns a (extension, content_type) string tuple. The `extension` field is used to filter the
            input files which this input handler can accept. The `content_type` helps parse the file formatted using
            a specifc rule. e.g. `txt` extension may be used two differently formatted log files one for SQL log and
            the other one for Apache Log. The 'content_type` can help distinguish this scenario and can apply the
            appropriate inout handler to parse the inoput.

        io() -> list[InputDescriptor]
            This method returns all the io available through the `input file` parsed by the handler. Each input
            has a name, its type and the shape if it's an array input. Please see
            `~algflow.io.input_handler.InputDescriptor` for more information.
    """

    @property
    @classmethod
    @abstractmethod
    def pathspec(cls) -> PathSpec:
        pass

    @abstractmethod
    def __init__(self, path: Path, **options):
        pass

    @property
    @abstractmethod
    def elements(self) -> DataElements:
        pass

    @abstractmethod
    def query(self, name: str, query: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def get(self, key: str) -> Any:
        pass

    def get_multi(self, *args: str) -> dict[str, Any]:
        return {arg: self.get(arg) for arg in args}

    @abstractmethod
    def set(self, name, value: Any):
        pass


class DataHandlerNotFound(Exception):
    def __init__(self, path: str):
        msg = f'handler for path `{path}` not registered'
        super().__init__(self, msg)


class DataHandlerNoPatterns(Exception):
    def __init__(self, targets: List[Type[AlgFlowDataHandler]], path: str):
        patterns = [h.pathspec.extension for h in targets]
        msg = f'No matching path patterns for the path `{path}`. Tried {patterns}'
        super().__init__(msg)


class DataHandlerConflict(Exception):
    def __init__(self, targets: List[Type[AlgFlowDataHandler]], path: str):
        msg = f'found {len(targets)} handler for input `{path}`'
        msg += ','.join([t.__name__ for t in targets])
        super().__init__(msg)


@dataclass(frozen=True)
class DataHandlerManager(Singleton):
    handlers: Dict[str, List[AlgFlowDataHandler]] \
        = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self):
        data_handler_entrypoints = entry_points()['algflow.data_handlers']
        for entry in data_handler_entrypoints:
            logger.info(f'adding data handlers {entry}')
            handler: AlgFlowDataHandler = entry.load()
            self.handlers[handler.pathspec.extension].append(handler)

    # scope helps with running two similar pipelines and routing the input to
    # appropriate pipeline instances. provisioned for future use.
    def get_handler(self, path: Optional[str] = None,
                    content_type: Optional[str] = None) -> Type[AlgFlowDataHandler]:
        if path:
            p = Path(path)
            if not p.suffix:
                raise DataHandlerNotFound(path)
            handlers = self.handlers.get(p.suffix[1:], [])
            targets = [h for h in handlers if h.pathspec.match(p.stem)]
            if len(targets) > 1:
                if content_type is not None:
                    # TODO: resolve using content_type
                    pass
                raise DataHandlerConflict(targets, path)
            elif len(targets) == 1:
                return targets[0]

        raise DataHandlerNotFound(path)
