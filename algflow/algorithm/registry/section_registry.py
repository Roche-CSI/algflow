import dataclasses
from typing import Dict, Any
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger('algflow.section_registry')


class SectionRegistrationInReadOnly(Exception):
    def __init__(self, alg_name: str, section: str):
        msg = f'{section} Registry for `{alg_name}` is read only. reset before registering'
        super().__init__(msg)


class SectionAlreadyRegistered(Exception):
    def __init__(self, alg_name: str, section: str):
        msg = f"section {section} for algorithm`{alg_name}` is already registered."
        super().__init__(msg)


class ClassNotFoundError(Exception):
    def __init__(self, class_name):
        self.class_name = class_name
        super().__init__(f'`{class_name}` is not defined')


@dataclasses.dataclass
class SectionRegistry:
    name: str
    variables: Dict[str, Any] = dataclasses.field(default_factory=lambda: {})
    classes: Dict[str, Any] = dataclasses.field(default_factory=lambda: {})

    def reset(self):
        self.variables = {}
        self.classes = {}

    def register_class(self, klass):
        alg_name = klass.__algorithm__
        if alg_name in self.classes:
            raise SectionAlreadyRegistered(alg_name, self.name)

        logger.warning(f'registering {alg_name} {self.name}')
        self.classes[alg_name] = klass

    def get_referenced_class(self, name):
        try:
            return self.classes[name]
        except KeyError:
            raise ClassNotFoundError(name)

    def register_variables(self, klass):
        for k, v in klass.__variables__.items():
            logger.warning(f'\tadding {v}')
            self.variables[k] = (klass, v)

    def get_variable(self, name):
        return self.variables[name]

    def register(self, klass: Any):
        alg_name = klass.__algorithm__
        logger.info(f'registry {self.name} {hex(id(self))} state {alg_name} {self.classes.keys()}')
        if alg_name in [self.name, 'Algorithm']:
            logger.info(f'skipping registration of `{alg_name}` as it is a base class')
            return

        self.register_class(klass)
        self.register_variables(klass)
