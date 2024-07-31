import logging
from typing import Any

from algflow.algorithm.alg_meta import AlgorithmMetaClass
from algflow.algorithm.output import Output

logger = logging.getLogger('Algorithm')


class AlgorithmError(Exception):
    def __init__(self, algo, err):
        self.algo = algo
        msg = 'Error in algorithm `%s`: %r'.format(algo, err)
        super(AlgorithmError, self).__init__(msg)


class Algorithm(metaclass=AlgorithmMetaClass):
    def __init__(self, params=None):
        self.params = params

    def run(self, inputs, outputs):
        raise NotImplementedError('This method must be implemented')

    # def init_input(self, storage):
    #     props = {}
    #     for name, trait in self.Input.traits().items():
    #         if storage.has(name):
    #             props[name] = storage.get(name)
    #     inputs = self.Input(**props)
    #     return inputs

    def debug(self, msg):
        logger.debug(f"Algorithm {self.algorithm}: {msg}")

    def info(self, msg):
        logger.info(f"Algorithm {self.algorithm}: {msg}")

    def warning(self, msg):
        logger.warning(f"Algorithm {self.algorithm}: {msg}")

    def __getstate__(self):
        p_state = self.params.__getstate__()
        i_state = self.inputs.__getstate__()
        o_state = self.outputs.__getstate__() if self.outputs else None
        return {'algorithm': self.algorithm, 'params': p_state, 'io': i_state, 'inout': o_state}

    def __call__(self, inputs: dict[str, Any]) -> dict[str, Any]:
        inputs = self.Input(**inputs)
        outputs = self.Output()
        self.run(inputs, outputs)
        outputs.validate()
        return outputs.__dict__
