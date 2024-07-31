from algflow.algorithm.input import InputSection
from algflow.algorithm.output import OutputSection
from algflow.algorithm.params import ParamSection


class SubclassingError(Exception):
    def __init__(self, name, bases):
        self.name = name
        self.bases = bases
        msg = f"Algorithm {name} derived from more than one algorithm"
        super().__init__(msg)


class AlgorithmMetaClass(type):
    @staticmethod
    def iter_alg_klass(alg_bases: tuple):
        for base in alg_bases:
            if isinstance(base, AlgorithmMetaClass):
                yield base

    def __new__(cls, name, bases, props):
        props['algorithm'] = name
        alg_bases = [b for b in cls.iter_alg_klass(bases)]
        meta_args = (name, alg_bases, props)
        props['Param'] = ParamSection(*meta_args)
        props['Input'] = InputSection(*meta_args)
        props['Output'] = OutputSection(*meta_args)

        AlgKlass = super().__new__(cls, name, bases, props)  # noqa
        return AlgKlass
