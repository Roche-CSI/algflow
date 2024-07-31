import logging
import dataclasses
from typing import Optional, Dict
from traits.has_traits import HasStrictTraits

from algflow.algorithm.section.variable import SectionVariable
from algflow.algorithm.section.metaclass import SectionMetaClass
from algflow.algorithm.section.main import Section
from algflow.inout.asset import Asset, remove_asset_from_props

logger = logging.getLogger('AlgOutput')


class MissingOutput(Exception):
    def __init__(self, anno, missing_outputs):
        self.anno = anno
        self.missing_outputs = missing_outputs
        missing = ', '.join(sorted(missing_outputs))
        msg = f'The outputs `{missing}` in annotator `{anno}` is missing'
        super().__init__(msg)


@dataclasses.dataclass
class OutputVariable(SectionVariable):
    """
    Output variables can accept asset specification.
    The asset will be created after the output becomes available.
    """
    asset: Optional[Asset] = None

    @classmethod
    # def process(cls, name, value) -> Optional[Self]:
    def process(cls, name, value):
        if isinstance(value, Asset):
            return cls(name, 'asset', asset=value)
        return None

    # def set_spec_from_trait(self, trait):
    #     super().set_spec_from_trait(trait)
    #     if trait.description is None:
    #         raise ValueError(f'No description for {trait}')
    #     return self


class OutputMetaClass(SectionMetaClass):
    section_name = 'Output'
    VariableClass = OutputVariable

    @classmethod
    def on_props(mcs, props):
        remove_asset_from_props(props)


class Output(HasStrictTraits, metaclass=OutputMetaClass):
    @classmethod
    def assets(cls) -> Dict[str, OutputVariable]:
        return {k: v for k, v in cls.iter_variables() if v.type == 'asset'}

    @classmethod
    def required(cls) -> Dict[str, OutputVariable]:
        return {k: v for k, v in cls.iter_variables() if v.required}

    @classmethod
    def optional(cls) -> Dict[str, OutputVariable]:
        return {k: v for k, v in cls.iter_variables() if not v.required}

    def validate(self):
        missing_required_output = [
            name
            for name in self._required
            if getattr(self, name, None) is None
        ]
        if missing_required_output:
            raise MissingOutput(self.parent, missing_required_output)

    @classmethod
    def iter_variables(cls):
        yield from cls.__variables__.items()


OutputSection = Section(Output)
