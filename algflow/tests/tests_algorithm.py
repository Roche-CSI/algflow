import unittest
import numpy as np

from algflow import Algorithm
from algflow.data import Int, Float, Array, Str
from algflow.algorithm.registry import algorithm_registry


class AlgorithmTests(unittest.TestCase):
    def assertAttr(self, attr, obj):
        testBool = hasattr(obj, attr)
        self.assertTrue(testBool, msg='obj lacking an attribute. obj: %s, intendedAttr: %s' % (obj, attr))

    def setUp(self) -> None:
        algorithm_registry.reset()

    def tearDown(self) -> None:
        pass

    def test_define_algorithm(self):
        class TestAlg(Algorithm):
            class Param:
                p = Int(default=4)

            class Input:
                d = Array(dtype=np.float, shape=(3,4))

            class Output:
                o = Float

            def run(self, inputs, outputs):
                outputs.o = np.sum(inputs.d) / inputs.p

        self.assertEqual(TestAlg.algorithm, 'TestAlg')
        self.assertAttr('Param', TestAlg)
        self.assertAttr('Input', TestAlg)
        self.assertAttr('Output', TestAlg)

    def test_invalid_input(self):
        class SmoothingAverage(Algorithm):
            class Param:
                window = Int(required=True)
                method = Str("shift")

            class Input:
                data = Array(dtype=np.float, meta={"category": "SBX", "priority": 2, })

            class Output:
                smoothed_avg = Float

            def run(self, inputs, outputs):
                data = inputs.data
                data = np.cumsum(data, dtype=float)
                n = self.params.window
                data[n:] = data[n:] - data[:-n]
                outputs.smoothed_avg = data / n

    def test_missing_input(self):
        pass

    def test_invalid_output(self):
        pass

    def test_missing_output(self):
        pass

    def test_dump_input(self):
        pass

    def test_dump_output(self):
        pass

    def test_precondition(self):
        pass


    # def test_param2(self):
    #     class SmoothingAverage(Algorithm):
    #         class Param:
    #             window = Int(4)
    #             method = Str("shift")
    #
    #         class Input:
    #             data = Array(dtype=np.float)
    #
    #         class Output:
    #             smoothed_avg = Float
    #
    #         def run(self, io, outputs):
    #             data = io.data
    #             data = np.cumsum(data, dtype=float)
    #             n = self.params.window
    #             data[n:] = data[n:] - data[:-n]
    #             outputs.smoothed_avg = data / n
    #
    #     SmoothingAverage.Param.init_shared_param()
    #     sm_param = SmoothingAverage.Param.shared
    #     self.assertIsNotNone(sm_param)
    #     self.assertEqual(sm_param.method, "shift")
    #     self.assertEqual(sm_param.window, 4)


if __name__ == '__main__':
    unittest.main()
