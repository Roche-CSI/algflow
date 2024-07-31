import unittest
from traits.api import Int, Float, Str, Dict
from traits.trait_errors import TraitError

from algflow import Algorithm
from algflow.algorithm.section.metaclass import ReservedKeywordError
from algflow.algorithm.registry import algorithm_registry
from algflow.algorithm.params import Param

from algflow.algorithm.params.errors import (
    ParamDeprecatedError, InvalidParamInOverride, ReferencedParamTypeError,
    ReferencedParamNotDefined
)
from algflow.algorithm.registry.section_registry import ClassNotFoundError, SectionAlreadyRegistered
from algflow.pipeline.param import PipelineParam, ParamStoreHier


class ParamTests(unittest.TestCase):
    def assertAttr(self, attr, obj):
        res = hasattr(obj, attr)
        self.assertTrue(res, msg=f'obj lacking an attribute. obj: {obj}, intendedAttr: {attr}')

    def setUp(self) -> None:
        algorithm_registry.reset()

    def tearDown(self) -> None:
        pass

    def test_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(4)
                method = Str("shift")
                description = Str

        sm_param = SmoothingAverage.Param.create(PipelineParam())
        self.assertEqual(sm_param.method, "shift")
        self.assertEqual(sm_param.window, 4)

    def test_defined_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(4)
                method = Str("shift")
                description = Str

        definition = [p.asdict() for p in SmoothingAverage.Param.defined().values()]
        EXPECTED_DEFINITION = [
            {'name': 'window', 'type': 'Int', 'ref': None, 'required': False, 'deprecated': False, 'aliases': [],
             'inherited': False},
            {'name': 'method', 'type': 'Str', 'ref': None, 'required': False, 'deprecated': False, 'aliases': [],
             'inherited': False},
            {'name': 'description', 'type': 'Str', 'ref': None, 'required': False, 'deprecated': False, 'aliases': [],
             'inherited': False}
        ]

        self.assertEqual(definition, EXPECTED_DEFINITION)
        sm_param = SmoothingAverage.Param.create(PipelineParam())

        self.assertIsNotNone(sm_param)
        self.assertEqual(sm_param.method, "shift")
        self.assertEqual(sm_param.window, 4)
        self.assertEqual(sm_param.description, '')

    def test_param_override(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(4)
                method = Str("shift")
                description = Str

        store = PipelineParam(data={"window": 10, "method": 'direct', "description": "calculate smooth average"})
        sm_param = SmoothingAverage.Param.create(store)
        self.assertEqual(sm_param.method, "direct")
        self.assertEqual(sm_param.window, 10)

    def test_invalid_param_override(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(4)
                method = Str("shift")
                description = Str

        store = PipelineParam(data={"description": 10})
        # `description` should be string
        EXPECTED_ERROR_MSG = "The 'description' trait of a Param<SmoothingAverage> instance must be a string"
        with self.assertRaisesRegex(TraitError, EXPECTED_ERROR_MSG):
            SmoothingAverage.Param.create(store)

    def test_required_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(required=True)
                method = Str("shift")
                description = Str("smoothing average")

        with self.assertRaisesRegex(TraitError, 'The following required traits were not provided: window'):
            SmoothingAverage.Param.create(PipelineParam())

    def test_param_mixins(self):
        class PropertySheet(Param):
            name = Str(required=True)
            description = Str("calculates smoothing average on an array")

        class SmoothingAverage(Algorithm):
            class Param:
                __mixins__ = [PropertySheet]
                window = Int(10)
                method = Str("shift")

        store = PipelineParam(data={"name": 'Smoothing Algorithm'})
        param = SmoothingAverage.Param.create(store)
        self.assertEqual(param.name, 'Smoothing Algorithm')
        self.assertEqual(param.description, 'calculates smoothing average on an array')

    def test_param_inheritance(self):
        class PropertySheet(Param):
            name = Str(required=True)
            description = Str("calculates smoothing average on an array")

        class SmoothingAverage(Algorithm):
            class Param:
                __mixins__ = [PropertySheet]
                window = Int(10)
                method = Str("shift")

        class SmoothingAverageAndVariance(SmoothingAverage):
            class Param:
                name = Str('SAV Algorithm')
                method = Str('piecewise')
                format = Str('jpg')

        store = PipelineParam(data={"window": 20})
        param = SmoothingAverageAndVariance.Param.create(store)
        self.assertEqual(param.name, 'SAV Algorithm')
        self.assertEqual(param.window, 20)
        self.assertEqual(param.method, 'piecewise')

    def test_param_alias(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(required=True, aliases=['win'], description='abc', meta={'a': 1})
                method = Str("shift")
                description = Str("smoothing average")

        store = PipelineParam(data={"win": 10, "method": 'direct', "description": "calculate smooth average"})
        param = SmoothingAverage.Param.create(store)
        self.assertEqual(param.window, 10)

    def test_deprecate_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(10)
                method = Str("shift", deprecated=True)
                description = Str("smoothing average")

        store = PipelineParam(data={"method": 'direct'})
        err_msg = 'The parameter `method` defined in algorithm `SmoothingAverage` is deprecated.'
        with self.assertRaisesRegex(ParamDeprecatedError, err_msg):
            SmoothingAverage.Param.create(store)

    def test_aliased_deprecate_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(10)
                method = Str("shift", aliases=['alg'],  deprecated=True)
                description = Str("smoothing average")

        store = PipelineParam(data={"alg": 'direct'})
        err_msg = 'The parameter `method` or `alg` defined in algorithm `SmoothingAverage` is deprecated.'
        with self.assertRaisesRegex(ParamDeprecatedError, err_msg):
            SmoothingAverage.Param.create(store)

    def test_hier_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(required=True, aliases=['win'])
                method = Str("shift", aliases=['alg'])
                description = Str("smoothing average")

        params = '''
        SmoothingAverage:
            win: 12
            alg: direct
        '''
        store = ParamStoreHier.create_from_string(params)
        param = SmoothingAverage.Param.create(store)
        self.assertEqual(param.window, 12)
        self.assertEqual(param.method, 'direct')

    def test_hier_param_invalid_class(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(required=True, aliases=['win'])
                method = Str("shift", aliases=['alg'])
                description = Str("smoothing average")

        params = '''
        SmoothingAverage:
            win: 12
            alg: direct
        
        CacheAlgorithm:
            most_recent: shift
            storage:
                a: 1
                b: 2
                c: 3
        '''
        with self.assertRaisesRegex(ClassNotFoundError, "`CacheAlgorithm` is not defined"):
            store = ParamStoreHier.create_from_string(params)
            param = SmoothingAverage.Param.create(store)

    def test_hier_param_extra_param(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(required=True, aliases=['win'])
                method = Str("shift", aliases=['alg'])
                description = Str("smoothing average")

        params = '''
        SmoothingAverage:
            win: 12
            alg: direct
            trailing: true
        '''
        err_msg = "The parameter `trailing` is not defined in algorithm `SmoothingAverage`"
        with self.assertRaisesRegex(InvalidParamInOverride, err_msg):
            store = ParamStoreHier.create_from_string(params)
            param = SmoothingAverage.Param.create(store)

    def test_standalone_param(self):
        class SmoothingParam(Param):
            window = Int(required=True)
            method = Str("shift", aliases=['alg'])
            description = Str("smoothing average")

        params = '''
        SmoothingParam:
            window: 12
            alg: direct
        '''
        store = ParamStoreHier.create_from_string(params)
        param = SmoothingParam.create(store)

        self.assertEqual(param.window, 12)
        self.assertEqual(param.method, 'direct')

    def test_param_class_duplication(self):
        def first_definition():
            class SmoothingParam(Param):
                window = Int(required=True)
                method = Str("shift", aliases=['alg'])
                description = Str("smoothing average")

        def second_definition():
            class SmoothingParam(Param):
                win = Int(required=True)
                method = Str("shift", aliases=['alg'])
                description = Str("smoothing average")

        with self.assertRaisesRegex(SectionAlreadyRegistered,
                                    'Param for class`SmoothingParam` is already registered'):
            first_definition()
            second_definition()

    def test_define_reserved_keyword(self):
        def reserve_keyword_definition():
            class SmoothingParam(Param):
                window = Int(required=True)
                method = Str("shift", aliases=['alg'])
                cname = Str("smoothing average")

        msg = '`cname` is a reserved keyword and cannot be used as a variable name in `SmoothingParam`'
        with self.assertRaisesRegex(ReservedKeywordError, msg):
            reserve_keyword_definition()

    def test_params_dag(self):
        def define_a():
            class A(Param):
                a1 = Int(required=True)
                a2 = Str("foo")

        def define_b():
            class B(Param):
                b1 = Float(required=True)
                b2 = Str("bar")
                a1 = Int(ref="A")

        def define_c():
            class C(Param):
                c1 = Int(required=True)
                c2 = Float(20)
                a2 = Str(ref="A")

        def define_d():
            class D(Param):
                d1 = Str(required=True)
                d2 = Str("alice")
                b1 = Float(ref="B")
                c1 = Int(ref="C")

        # now lets define all the classes in reverse order
        define_d()
        define_c()
        define_b()
        define_a()

        data = {'a1': 10, 'b1': 20.0, 'c1': 30, 'd1': "foo-bar"}
        store = PipelineParam(data=data)
        store.init_params()
        a = store.get_param_set("A")
        self.assertEqual((a.a1, a.a2), (10, "foo"))

        b = store.get_param_set("B")
        self.assertEqual((b.b1, b.b2, b.a1), (20.0, "bar", 10))

        c = store.get_param_set("C")
        self.assertEqual((c.c1, c.c2, c.a2), (30, 20.0, "foo"))

        d = store.get_param_set("D")
        self.assertEqual((d.d1, d.d2, d.b1, d.c1), ("foo-bar", "alice", 20.0, 30))

    def test_referenced_param_iterator(self):
        class Storage(Algorithm):
            class Param:
                cache = Dict()

        class CacheAlgorithm(Algorithm):
            class Param:
                most_recent = Str('shift')
                cache = Dict(ref='Storage')

        references = [p.asdict() for p in CacheAlgorithm.Param.referenced().values()]
        EXPECTED_REFERENCES = [
            {'name': 'cache',
             'type': 'Dict',
             'ref': 'Storage',
             'required': False,
             'deprecated': False,
             'aliases': [],
             'inherited': False}
        ]
        self.assertEqual(references, EXPECTED_REFERENCES)

    def test_referenced_param_missing_source(self):
        from algflow.algorithm.params.errors import ReferencedParamSetNotFound

        class CacheAlgorithm(Algorithm):
            class Param:
                most_recent = Str('shift')
                cache = Dict(ref='Storage')

        with self.assertRaises(ReferencedParamSetNotFound):
            CacheAlgorithm.Param.create(PipelineParam())

    def test_incompatible_references(self):
        class A(Algorithm):
            class Param:
                a = Int(required=True)

        class B(Algorithm):
            class Param:
                a = Float(ref='A')
                b = Str('shift')

        store = PipelineParam(data={'a': 10})
        with self.assertRaisesRegex(ReferencedParamTypeError, "expecting `Int` for parameter `a`"):
            store.init_params()

    def test_referenced_param_name_mismatch(self):
        class A(Algorithm):
            class Param:
                a = Int(required=True)

        class B(Algorithm):
            class Param:
                a1 = Int(ref='A')
                b = Str('shift')

        store = PipelineParam(data={'a': 10})
        msg = "parameter `a1` for algorithm `B` not defined in referenced algorithm/param class `A`"
        with self.assertRaisesRegex(ReferencedParamNotDefined, msg):
            store.init_params()

    def test_param_cmdline(self):
        pass

    def test_param_arg_name_overrides(self):
        pass

if __name__ == '__main__':
    unittest.main()
