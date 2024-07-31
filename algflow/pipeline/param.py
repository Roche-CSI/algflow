import dataclasses
import logging
from typing import Dict, Any, Type
import networkx as nx

from algflow.algorithm.params.dag import ParamDag
from algflow.algorithm.params.errors import ReferencedParamSetNotFound
from algflow.algorithm.params import Param
from algflow.pipeline.param_override import ParamOverride
from algflow.algorithm.params.param_variable import ParamVariable
from algflow.algorithm.registry import AlgorithmRegistry
from algflow.algorithm.types import AlgName
from algflow.data.container import DataContainer

logger = logging.getLogger('algflow.pipeline.param')


# TODO: Add support for multiple data containers later
@dataclasses.dataclass
class PipelineParam:
    container: DataContainer = dataclasses.field(default_factory=lambda: DataContainer.empty('param'))
    _data: Dict[str, Any] = dataclasses.field(default_factory=dict)  # raw data
    _params: Dict[AlgName, Param] = dataclasses.field(default_factory=dict)  # resolved params

    def __post_init__(self):
        self._data = self.container.handler.get()

    def get(self, *args: str) -> Dict[str, Any]:
        print('DATA query:', self._data)
        result: Dict[str, Any] = {}

        for key in args:
            try:
                result[key] = self._data[key]
            except KeyError:
                pass
        return result

    def get_ref_value(self, variable: ParamVariable) -> Any:
        if variable.ref:
            param_set = self.get_param_set(variable.ref)
            return getattr(param_set, variable.name, None)
        return None

    def get_references(self, param_klass: Type[Param]) -> Dict[str, Any]:
        return {k: self.get_ref_value(v) for k, v in param_klass.referenced().items()}

    # If some algorithm references a parameter defined by another algorithm,
    # then this function will be used to resolve the reference.
    def get_param(self, alg_name: AlgName) -> Param:
        try:
            return self._params[alg_name]
        except KeyError:
            raise ReferencedParamSetNotFound(alg_name)

    def create(self, param_klass: Type[Param]) -> Param:
        alg_name: AlgName = param_klass.__algorithm__
        referenced = self.get_references(param_klass)

        overrides = ParamOverride(param_klass, data=self._data)
        logger.info(f'PARAMS: referenced={referenced} overrides={overrides.data}')
        param = param_klass(**referenced, **overrides.data)
        self._params[alg_name] = param
        return param

    def __post_init__(self):
        # print(graph)
        logger = logging.getLogger("param dag")
        classes = AlgorithmRegistry().get_section_registry('Param').classes
        dag = ParamDag(classes)
        for node in nx.topological_sort(dag):
            logger.info(f"iterating node: {node}")
            param_class = dag.nodes[node]['param_class']
            logger.info(f'dag initializing {param_class}')
            self.create(param_class)

# class ParamStoreHier(ParamStore):
#     @classmethod
#     def create_from_string(cls, params: str):
#         data = yaml.safe_load(params)
#         return cls(data=data)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         param_registry = algorithm_registry.get_section_registry('Param')
#         for alg, overrides in self._data.items():
#             param_class = param_registry.get_referenced_class(alg)
#             self._data[alg] = param_class.validate(overrides, check_extra=True)

    # def get_override(self, alg_name: str) -> Dict[str, Any]:
    #     return self._data.get(alg_name, ParamOverride(data={}, validated=True))
