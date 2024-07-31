from __future__ import annotations
import dataclasses
import logging
from typing import List, Any
from algflow.algorithm.section.variable import SectionVariable

logger = logging.getLogger('algflow.params.variable')


def debug_ref_param(method):
    def interceptor(ref, *args, **kwargs):
        v = method(ref, *args, **kwargs)
        logger.info(f'resolved {ref.name} to {v}')
        return v

    return interceptor


@dataclasses.dataclass
class ParamVariable(SectionVariable):
    ref: str = None
    deprecated: bool = False
    aliases: List[str] = dataclasses.field(default_factory=lambda: [])

    # TODO: Can be deleted in favor of ParamStore.resolve_references
    # @debug_ref_param
    # def get_ref_value(self, store):
    #     param_set = store.get_param_set(self.ref)
    #     return getattr(param_set, self.name, None)

    def set_spec_from_fwd_prop(self, prop):
        super().set_spec_from_fwd_prop(prop)
        self.ref = prop.metadata.get('ref', None)
        self.aliases = prop.metadata.get('aliases', [])

    def set_spec_from_trait(self, trait):
        super().set_spec_from_trait(trait)
        self.ref = trait.ref
        self.aliases = trait.aliases or []
        self.deprecated = trait.deprecated or False

    # def translate_aliases(self, data, alg_name=''):
    #     for alias in self.aliases:
    #         if alias in data:
    #             logger.info(f'renaming parameter {alias} to {self.name} in algorithm {alg_name}')
    #             data[self.name] = data[alias]
    #             del data[alias]

    def get_with_aliases(self, data: dict[str, Any]) -> Any:
        try:
            return data[self.name]
        except KeyError:
            for alias in self.aliases:
                try:
                    return data[alias], alias
                except KeyError:
                    pass
        raise KeyError(f'parameter {self.name} not found in data')
