import dataclasses
import logging
from typing import Type
from importlib.metadata import entry_points

from algflow import Algorithm
from algflow.common import Singleton
from algflow.algorithm.registry.section_registry import SectionRegistry
from rich import print

logger = logging.getLogger('algflow.algorithm_registry')


class AlgorithmNotFoundError(Exception):
    def __init__(self, output_name):
        self.output_name = output_name
        super().__init__(f'`algorithm not found for output {output_name}')


@dataclasses.dataclass
class AlgorithmRegistry(Singleton):
    sections: dict[str, SectionRegistry] = dataclasses.field(default_factory=lambda: {})
    algorithms: dict[str, Type[Algorithm]] = dataclasses.field(default_factory=lambda: {})

    def __post_init__(self):
        try:
            algorithm_entrypoints = entry_points()['algflow.algorithms']
        except KeyError:
            logger.warning('No algorithm entrypoints found')
        else:
            for entry in algorithm_entrypoints:
                logger.warning(f'adding algorithm {entry.name} - {entry.value}')
                alg = entry.load()
                self.register_algorithm(alg, entry.name, entry.value)

    def register_algorithm(self, klass: Type[Algorithm], name: str, module_path: str):
        if klass.algorithm in self.algorithms:
            raise Exception(f'Algorithm {klass.algorithm} already registered. Please rename your '
                            f'algorithm.')
        self.algorithms[klass.algorithm] = klass
        self.get_section_registry('Input').register(klass.Input)
        self.get_section_registry('Output').register(klass.Output)
        self.get_section_registry('Param').register(klass.Param)

    def get_algorithm(self, name: str) -> Type[Algorithm]:
        return self.algorithms[name]

    def get_algorithm_for_output(self, name: str) -> Type[Algorithm]:
        klass, _ = self.sections['Output'].get_variable(name)
        return self.algorithms[klass._parent]

    def get_section_registry(self, section_name: str) -> SectionRegistry:
        if section_name not in self.sections:
            self.sections[section_name] = SectionRegistry(section_name)

        return self.sections[section_name]

    def reset(self):
        logger.info(f'Resetting Algorithm Registry {hex(id(self))} ')
        for value in self.sections.values():
            value.reset()

