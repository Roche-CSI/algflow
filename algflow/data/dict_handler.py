# This class defines a dict based AlgFlowDataHandler which provides
# uniform input interface to the algorithms abstraction layer.
from typing import Dict, Any

from algflow.data.handler import AlgFlowDataHandler, PathSpec, DataElements


class DictHandler(AlgFlowDataHandler):

    @classmethod
    def pathspec(cls) -> PathSpec:
        return ""

    content_type = 'text/json'
    _data: Dict[str, Any]

    def __init__(self, *args, **kwargs):
        self._data: dict[str: Any] = {}
        initial_data = kwargs.get('data', None)
        if initial_data and isinstance(initial_data, dict):
            self._data = {**initial_data}
        super().__init__(self)

    def get(self, *args: str) -> Dict[str, Any]:
        print('DATA query:', self._data)
        result: Dict[str, Any] = {}

        for key in args:
            try:
                result[key] = self._data[key]
            except KeyError:
                pass
        return result

    def set(self, key: str, value: Any):
        self._data[key] = value

    @property
    def elements(self) -> DataElements:
        pass

    def query(self, name: str, query: Dict[str, Any]) -> Any:
        return None