from abc import ABC, abstractmethod
from typing import Any
import networkx as nx
from algflow.pipeline.main import AlgFlowPipeline


class PipelineExecutor(ABC):
    @abstractmethod
    def execute(self, **options) -> Any:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class SimplePipelineExecutor(PipelineExecutor):
    def __init__(self, pipeline: AlgFlowPipeline):
        self.pipeline = pipeline

    def execute(self, **options) -> Any:
        store = self.pipeline.store
        params = self.pipeline.params
        dag = self.pipeline.dag
        # execute the dag
        for node_name in nx.topological_sort(dag):
            node = dag.nodes[node_name]
            print('Visiting node:', node_name, node.keys(), node.values())
            if node.get('type') == 'algorithm':
                alg_klass = dag.algorithms[node_name]
                alg_params = params.get_param(node_name)
                inputs = {k: store.get(k) for k, v in alg_klass.Input.__variables__.items()}
                alg_instance = alg_klass(alg_params)
                outputs = alg_instance(inputs)
                store.set_multi(outputs)
            else:
                print('Ignoring node:', node_name)

    def __str__(self):
        return f"SimplePipelineExecutor(pipeline={self.pipeline})"
