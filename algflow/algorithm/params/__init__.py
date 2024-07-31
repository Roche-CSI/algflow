from __future__ import annotations

from typing import Dict, Any

from traits.has_traits import HasRequiredTraits

from algflow.algorithm.params.param_variable import ParamVariable
from algflow.algorithm.section.main import Section
from algflow.algorithm.section.metaclass import SectionMetaClass


class ParamMetaClass(SectionMetaClass):
    section_name = 'Param'
    VariableClass = ParamVariable


class Param(HasRequiredTraits, metaclass=ParamMetaClass):
    @classmethod
    def referenced(cls) -> Dict[str, ParamVariable]:
        return {k: v for k, v in cls.__variables__.items() if v.ref}

    @classmethod
    def defined(cls) -> Dict[str, ParamVariable]:
        return {k: v for k, v in cls.__variables__.items() if not v.ref}

    def get_override(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for key in self.defined().keys():
            try:
                value = self.trait_get(key)
                trait = self.trait(key)
                if trait.default != value:
                    d[key] = value
            except KeyError:
                pass  # this param is not overridden
        return d


ParamSection = Section(Param, True)
