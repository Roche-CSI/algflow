from dataclasses import dataclass, field
from typing import Dict, Any, List

from algflow.common import Singleton
from algflow.data.cache import DataCache
from algflow.data.container import DataContainer
from algflow.data.handler import DataElements
from algflow.data.spec import AlgFlowDataDescriptor


class DataElementNotFound(Exception):
    def __init__(self, name: str):
        msg = f'requested input {name} not provided by any input handlers'
        super().__init__(self, msg)


@dataclass(frozen=True)
class DataStore:
    cache: DataCache = field(default_factory=DataCache)
    routes: Dict[str, DataContainer] = field(default_factory=dict)
    data_containers: Dict[str, DataContainer] = field(default_factory=dict)
    elements: Dict[str, AlgFlowDataDescriptor] = field(default_factory=dict)

    def add_container(self, container: DataContainer, elements: DataElements):
        if container.path not in self.data_containers:
            self.data_containers[container.path] = container
            for e in elements:
                self.routes[e.name] = container
                self.elements[e.name] = e
        else:
            raise ValueError(f'container with path {container.path} already exists')

    def _get_container_for_element(self, name: str) -> DataContainer:
        try:
            return self.routes[name]
        except KeyError:
            raise DataElementNotFound(name)

    def get(self, name) -> Any:
        print('STORE GET:', name)
        try:
            return self.cache.get(name)
        except KeyError:
            container = self._get_container_for_element(name)
            value = container.handler.get(name)
            self.cache.set(name, value)
            return value

    def query(self, name: str, **kwargs) -> Any:
        container = self._get_container_for_element(name)
        # TODO: cache the query result
        return container.handler.query(name, **kwargs)

    def set_multi(self, data: Dict[str, Any]):
        for name, value in data.items():
            self.set(name, value)

    def set(self, name: str, value: Any) -> Any:
        self.cache.set(name, value, False)

    def flush_cache(self):
        for name, entry in self.cache.iter_dirty_entries():
            container = self._get_container_for_element(name)
            container.handler.set(name, entry.data)
            entry.flushed = True
