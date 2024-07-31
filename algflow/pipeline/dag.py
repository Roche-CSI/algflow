import dataclasses
from typing import Dict, Any, Type

import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

from algflow import Algorithm
from algflow.algorithm.registry import AlgorithmRegistry
from algflow.data.handler import DataElements
from algflow.data.store import DataStore
from rich import print


@dataclasses.dataclass
class PipelineDAG(nx.DiGraph):
    algorithms: Dict[str, Any]
    inputs: Dict[str, Any]

    def __init__(self, outputs: DataElements):
        super().__init__()
        self.algorithms = {}
        self.inputs = {}
        self.volatiles = set()
        self.gen_hybrid_graph(outputs)

    def gen_task_graph(self, outputs: DataElements):
        print('PD:', outputs)
        self.add_node('end')
        computations = [(element.name, 'end') for element in outputs]
        while len(computations) > 0:
            element_name, next_task = computations.pop(0)
            print('C:', element_name, next_task)
            try:
                alg = AlgorithmRegistry().get_algorithm_for_output(element_name)
            except KeyError:
                if next_task == 'end':
                    raise ValueError(f'Output {element_name} not provided by any algorithm.')
                else:
                    # since no algorithm is found, it must be an input
                    self.inputs[element_name] = next_task
                    self.add_node(element_name, type='input')
                    self.add_edge(element_name, next_task)
            else:
                if alg not in self.algorithms:
                    self.add_node(alg.algorithm, type="algorithm")
                    self.algorithms[alg.algorithm] = alg
                    for input in alg.Input.__variables__.values():
                        computations.append((input.name, alg.algorithm))
                    for output in alg.Output.__variables__.values():
                        if output.name not in self.nodes:
                            self.volatiles.add(output.name)
                self.add_edge(alg.algorithm, next_task, output=element_name)

    def gen_hybrid_graph(self, outputs: DataElements):
        deps = []
        for element in outputs:
            self.add_node(element.name, type='output', style='filled rounded')
            deps.append((element.name, None))
        print('DEPS:', deps)
        while len(deps) > 0:
            element_name, next_task = deps.pop(0)
            try:
                alg = AlgorithmRegistry().get_algorithm_for_output(element_name)
            except KeyError:
                if next_task is None:
                    raise ValueError(f'Output {element_name} not provided by any algorithm.')
                else:
                    # since no algorithm is found, it must be an input
                    self.create_input_node(element_name, next_task)
            else:
                if alg not in self.algorithms:
                    self.create_alg_node(alg)
                    deps += self.add_input_to_deps(alg)
                    self.connect_output_to_alg(alg)
                if next_task is not None:
                    self.add_edge(element_name, next_task)

    def create_input_node(self, input: str, next_task: str):
        self.inputs[input] = next_task
        self.add_node(input, type='input', shape='c', color='green')
        self.add_edge(input, next_task)

    def create_alg_node(self, alg: Type[Algorithm]):
        self.add_node(alg.algorithm, type="algorithm", color='red')
        self.algorithms[alg.algorithm] = alg

    def connect_output_to_alg(self, alg: Type[Algorithm]):
        for _, output in alg.Output.iter_variables():
            if output.name not in self.nodes:
                self.add_node(output.name, type='volatile')
            self.add_edge(alg.algorithm, output.name)

    @staticmethod
    def add_input_to_deps(alg: Type[Algorithm]):
        return [(input.name, alg.algorithm) for _, input in alg.Input.iter_variables()]

    def print(self):
        print(self)
        print('N:', self.nodes)
        print('E:', self.edges)

    def show(self):
        print('N:', self.nodes)
        print('E:', self.edges)
        layout = graphviz_layout(self, prog='dot', args='-Grankdir="LR"')
        colors = [self.nodes[n].get('color', 'blue') for n in self.nodes]
        # node_color=color_vector,
        nx.draw_networkx_nodes(self, pos=layout, node_color=colors, node_shape='s', node_size=1000)
        nx.draw_networkx_edges(self, pos=layout, edgelist=self.edges(), arrows=True)
        nx.draw_networkx_labels(self, pos=layout, font_size=8, font_color="black")

        plt.show()

