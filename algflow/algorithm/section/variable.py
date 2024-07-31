from __future__ import annotations
import logging
import dataclasses
from typing import Dict, Any, Iterator, Optional, Self

from traits.trait_type import TraitType
from traits.traits import ForwardProperty
from algflow.data.spec import DataVariable
from rich.logging import RichHandler

# FORMAT = "%(message)s"
# logging.basicConfig(
#     level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
# )
logger = logging.getLogger('SectionVariable')


@dataclasses.dataclass
class SectionVariable(DataVariable):
    required: bool = False
    inherited: bool = False

    def from_base(self) -> Self:
        return dataclasses.replace(self, inherited=True)

    def set_spec_from_fwd_prop(self, prop):
        assert isinstance(prop, ForwardProperty)
        return self

    def set_spec_from_trait(self, trait: TraitType) -> Self:
        assert isinstance(trait, TraitType)
        self.set_numpy_props(trait)
        self.required = trait.required or False
        return self

    def asdict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def process(cls, name: str, value: Any) -> Optional[Self]:
        logger.info(f'processing: {name}: {value} -> None')
        return None

    @classmethod
    def iter_variable(cls, props: Dict[str, Any]) -> Iterator[Self]:
        def typeof(v):
            return v.__class__.__name__

        def is_a_class(v):
            return isinstance(v, type)

        for name, value in props.items():
            logger.info(f'processing: {name}: {value}')
            if is_a_class(value) and issubclass(value, TraitType):
                obj = cls(name, value.__name__)
                obj.set_spec_from_trait(value())
            elif isinstance(value, ForwardProperty):
                obj = cls(name, typeof(value.handler))
                obj.set_spec_from_fwd_prop(value)
            elif isinstance(value, TraitType):
                logger.info(f'yielding {name}: {value}')
                obj = cls(name, typeof(value))
                obj.set_spec_from_trait(value)
            else:
                obj = cls.process(name, value)

            if obj:
                yield obj
