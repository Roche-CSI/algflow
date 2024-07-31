from __future__ import annotations
import logging
from typing import Dict, Any, Tuple
from traits.has_traits import MetaHasTraits

logger = logging.getLogger('algflow.SectionMetaClass')


def class_members(cls):
    return [k for k in cls.__dict__ if not k.startswith('__')]


def debug_print(name, bases, props):
    logger.info(f'Meta<{name}>:')
    logger.info(f'\tBase: {[b.__class__.__name__ for b in bases]}')
    logger.info(f'\tProps: {list(props.keys())}')


class ReservedKeywordError(Exception):
    def __init__(self, context, alg_name):
        msg = f"`cname` is a reserved keyword and cannot be used as a variable name in `{alg_name}`"
        super().__init__(msg)


class SectionMetaClass(MetaHasTraits):
    section_name = 'generic'
    VariableClass = None

    # @classmethod
    # @property
    # def section_registry(mcs) -> SectionRegistry:
    #     return algorithm_registry.get_section_registry(mcs.section_name)

    @classmethod
    def on_props(mcs, props: Dict[str, Any]):
        pass

    @classmethod
    def adjust_props(mcs, name: str, bases: Tuple[type, ...], props:  Dict[str, Any]):
        cname = props.get('_parent', name)
        if '__algorithm__' in props:
            raise ReservedKeywordError(mcs.__name__, cname)
        props['__algorithm__'] = cname
        props['__variables__'] = mcs.get_variables(bases, props)
        mcs.on_props(props)

    def __new__(mcs, name: str, bases: Tuple[type, ...], props:  Dict[str, Any]):
        # debug_print(name, bases, props)
        mcs.adjust_props(name, bases, props)
        # debug_print(name, bases, props)
        klass = super().__new__(mcs, name, bases, props)
        # mcs.section_registry.register(klass)
        return klass

    @classmethod
    def get_variables(cls, bases: Tuple[type, ...], props: Dict[str, Any]) -> (Dict[str, Any]):
        variables = {}
        for base in bases:
            if isinstance(base, cls):
                variables.update(base.__variables__)

        # for v in cls.VariableClass.iter_variable(props):
        #     print(f' ----> {v}')
        #     variables.update({v.name: v})
        variables.update({v.name: v for v in cls.VariableClass.iter_variable(props)})
        return variables
