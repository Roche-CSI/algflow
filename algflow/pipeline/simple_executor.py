import os
import traceback
from abc import ABC, abstractmethod
from typing import Any, Type
import networkx as nx

from algflow import Algorithm
from algflow.data.handler import DataHandlerManager
from algflow.pipeline.main import AlgFlowPipeline
from algflow.algorithm.events import (
    AlgflowEvent, ExecutionStartEvent, ExecutionErrorEvent,
    ExecutionEndEvent
)
from algflow.data.container import DataContainer
from dataclasses import field



class AlgorithmExecutor:
    def __init__(self, capture_events=True):
        self.capture_events = capture_events
        self.events = []

    @abstractmethod
    def run(self, algorithm: Type[Algorithm]) -> dict[str, Any]:



class PipelineExecutor(ABC):
    @abstractmethod
    def execute(self, **options) -> Any:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class SimplePipelineExecutor(PipelineExecutor):
    sys_routes: dict[str, DataContainer] = field(default_factory=dict)

    def __init__(self, pipeline: AlgFlowPipeline):
        self.pipeline = pipeline
        event_handler_klass = DataHandlerManager().get_handler("system.events", "events")
        self.event_handler = event_handler_klass(path="logs/events", scope='system')
        # TODO: ideate the event Data Handler
        self.sys_routes = {'events': DataContainer('events', None)}

    def emit(self, event: AlgflowEvent):
        self.event_handler.push('events', event)

    def execute(self, **options) -> Any:
        store = self.pipeline.store
        params = self.pipeline.params
        dag = self.pipeline.dag

        task_data = {
            'pid': os.getpid(),
            'run_id': self.run_id,
        }
        # execute the dag
        for node_name in nx.topological_sort(dag):
            node = dag.nodes[node_name]
            print('Visiting node:', node_name, node.keys(), node.values())
            if node.get('type') == 'algorithm':
                alg_klass = dag.algorithms[node_name]
                alg_params = params.get_param(node_name)
                inputs = {k: store.get(k) for k, v in alg_klass.Input.__variables__.items()}

                alg_instance = alg_klass(alg_params, capture_events=False)
                computation = alg_instance(inputs)

                try:
                    self.emit(ExecutionStartEvent(node_name, task_data))
                    while True:
                        event = next(computation)
                        if isinstance(event, AlgflowEvent):
                            self.event_handler.push('events', event)
                except StopIteration as e:
                    outputs = e.value
                    store.set_multi(outputs)
                except Exception as e:
                    # save dag and input/output state
                    # generate debug info
                    # generate ExecutionError
                    debug_info = {'error': str(e), 'stack_trace': traceback.format_exc()}
                    self.emit(ExecutionErrorEvent(node_name, debug_info))
                    raise e
                finally:
                    self.emit(ExecutionEndEvent(node_name, task_data))
                    pass
            else:
                print('Ignoring node:', node_name)

    def __str__(self):
        return f"SimplePipelineExecutor(pipeline={self.pipeline})"
