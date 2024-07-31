import dataclasses
import logging
from pathlib import Path

import yaml
from typing import List, Dict, Optional

from algflow.pipeline.param import PipelineParam
from algflow.data.container import DataContainer
from algflow.data.handler import DataElements
from algflow.data.spec import AlgFlowDataDescriptor
from algflow.data.store import DataStore
from algflow.algorithm.registry import AlgorithmRegistry
from algflow.pipeline.dag import PipelineDAG

logger = logging.getLogger('algflow.pipeline')


@dataclasses.dataclass
class AlgFlowPipeline:
    params: PipelineParam = dataclasses.field(default_factory=PipelineParam)
    store: DataStore = dataclasses.field(default_factory=DataStore)
    dag: Optional[PipelineDAG] = None

    def init_params(self, params_file: Path):
        self.params = PipelineParam(DataContainer('param', params_file))

    # inputs:
    #  - path: /path/to/input
    #    content_type: csv
    #    scope: global
    # -  path: /path/to/input
    #    content_type: csv
    #    scope: global

    def process_inputs(self, inputs: List[Dict[str, str]]):
        for input in inputs:
            container = DataContainer(
                'input',
                input['path'],
                input.get('content_type', None),
                input.get('scope', None)
            )
            self.store.add_container(container, container.handler.elements())

    # outputs:
    #  - path: /path/to/output
    #    content_type: csv
    #    scope: global
    #    elements:
    #      - output1
    #      - output2
    #      - output3
    #      - output4
    def process_outputs(self, outputs: list[dict[str, str]]) -> List[AlgFlowDataDescriptor]:
        all_elements = []
        for output in outputs:
            container = DataContainer(
                'output',
                output['path'],
                output.get('content_type', None),
                output.get('scope', None)
            )
            elements, _ = self.get_data_elements(output['elements'])
            self.store.add_container(container, elements)
            all_elements.extend(elements)
        return all_elements

    @staticmethod
    def get_data_elements(element_names: list[str]) -> tuple[DataElements, set]:
        elements: List[AlgFlowDataDescriptor] = []
        klasses = set()
        output_registry = AlgorithmRegistry().get_section_registry('Output')
        for element_name in element_names:
            try:
                klass, v = output_registry.get_variable(element_name)
                elements.append(AlgFlowDataDescriptor.from_variable(v))
                klasses.add(klass)
            except KeyError:
                raise ValueError(f'Output {element_name} not provided by any algorithm.')
        return elements, klasses

    def match_inputs(self):
        # just matching the name for now
        for input_name, source in self.dag.inputs.items():
            if input_name in self.store.routes:
                input_desc = self.store.elements[input_name]
                source_desc = source.Input.__variables__[input_name]
                if input_desc.type is not None and input_desc.type != source_desc.type:
                    raise ValueError(f'Type mismatch for input {input_name}')
                else:
                    logger.log('skipping type matching for {input_name}')
            else:
                raise ValueError(f'Could not find the Input `{input_name}`')

    # TODO: Current Assumption: All the outputs are explicitly specified by name
    # TODO: Need to add support for output query language
    @classmethod
    def create(cls, inputs: list[str], outputs: list[str], out_file: str,
               params_file: Path | None = None):
        pipeline = cls()
        pipeline.init_params(params_file)

        inputs = [{'path': input} for input in inputs]
        outputs = [{'path': out_file, 'elements': outputs}]
        pipeline.process_inputs(inputs)
        elements = pipeline.process_outputs(outputs)
        pipeline.dag = PipelineDAG(elements)
        return pipeline

    @classmethod
    def create_from_yaml(cls, yaml_file: str):
        pipeline_data = yaml.load(yaml_file)
        pipeline = cls()
        pipeline.process_inputs(pipeline_data['inputs'])
        elements = pipeline.process_outputs(pipeline_data['outputs'])
        pipeline.params = PipelineParam(
            DataContainer.create_dict_data_container('param', pipeline_data['params']))
        pipeline.dag = PipelineDAG(elements)
        return pipeline
