import logging
from typing import Any
import networkx as nx

from algflow.algorithm.params.errors import ReferencedParamTypeError, ReferencedParamNotDefined, ParamSourceError
from algflow.algorithm.params import Param

logger = logging.getLogger('param dag')


class ParamDag(nx.DiGraph):
    def __init__(self, classes: dict[str, Param]):
        super().__init__()
        for alg, param_class in classes.items():
            logger.info(f'adding [bold red]{alg}[/] node')
            # node names are algorithms
            self.add_node(alg, param_class=param_class)
            logger.info(f"node: {self.nodes[alg]}")
            for param in param_class.referenced().values():
                try:
                    # reference is also algorithm name
                    ref_class = classes[param.ref]
                    try:
                        def_p = ref_class.defined()[param.name]
                        if param.type != def_p.type:
                            raise ReferencedParamTypeError(alg, param, def_p)
                    except KeyError:
                        raise ReferencedParamNotDefined(alg, param)
                    # verification complete, add the edge to class referencing it
                    self.add_edge(param.ref, alg)
                except KeyError:
                    raise ParamSourceError(alg, param)
        logger.info(f'dag={self.nodes}')
