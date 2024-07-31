from __future__ import annotations

import dataclasses
import logging

from traits.has_traits import HasRequiredTraits
from typing import Dict, Optional, Any, List

from algflow.algorithm.section.variable import SectionVariable
from algflow.algorithm.section.metaclass import SectionMetaClass
from algflow.algorithm.section.main import Section
from algflow.inout.asset import Asset, remove_asset_from_props

logger = logging.getLogger('AlgInput')


@dataclasses.dataclass
class InputVariable(SectionVariable):
    """
    InputVariable is a SectionVariable that is used to define the input of an algorithm.
    In addition to the attributes inherited from SectionVariable, we can also define the following
     attributes:
        - alias: str, the input in the file may have a different name than the variable name. We can
            use alias to specify the name of the input in the file.
        - param: List[str], Some io can be parameterized, e.g. there can be multiple cells in a file,
            and we want to specify which cell to use. We can use param to specify the cell name.
            e.g.  param = ['$cell_id']
        - query: Dict, Some input may need be created from multiple fields or io present in
            the input source. We can use `query` to specify how to access/construct the input.
            e.g. query = {'$path': '/cells/$cell_id'}
        - pipeline: str, Some input may need to be transformed before it can be used.
            We can use pipeline to specify the transformations performed to generate the input dynamically.
    """
    pipeline: str = None
    alias: str = None
    param: List[str] = None
    query: Dict = None
    scope: str = None
    asset: Optional[Asset] = None

    def set_spec_from_fwd_prop(self, prop: Dict[str, Any]):
        super().set_spec_from_fwd_prop(prop)
        self.pipeline = prop.metadata.get('pipeline', None)
        self.alias = prop.metadata.get('alias', None)
        self.param = prop.metadata.get('param', None)
        self.query = prop.metadata.get('query', None)
        self.query = prop.metadata.get('scope', None)

    def set_spec_from_trait(self, trait):
        super().set_spec_from_trait(trait)
        self.pipeline = trait.pipeline
        self.args = trait.args or -1

    @classmethod
    #  def process(cls, name, value) -> Optional[Self]:
    def process(cls, name, value):
        if isinstance(value, Asset):
            return cls(name, 'asset', asset=value)
        return None


class InputMetaClass(SectionMetaClass):
    section_name = 'Input'
    VariableClass = InputVariable

    @classmethod
    def on_props(mcs, props: Dict[str, Any]):
        remove_asset_from_props(props)


class Input(HasRequiredTraits, metaclass=InputMetaClass):
    @classmethod
    def assets(cls) -> Dict[str, InputVariable]:
        return {k: v for k, v in cls.iter_variables() if v.type == 'asset'}

    @classmethod
    def required(cls) -> Dict[str, InputVariable]:
        return {k: v for k, v in cls.iter_variables() if v.required}

    @classmethod
    def optional(cls) -> Dict[str, InputVariable]:
        return {k: v for k, v in cls.iter_variables() if not v.required}

    @classmethod
    def iter_variables(cls):
        yield from cls.__variables__.items()


InputSection = Section(Input)
