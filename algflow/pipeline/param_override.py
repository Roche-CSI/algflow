import dataclasses
import logging
from typing import Type, Dict, Any

from algflow.algorithm.params.errors import ParamDeprecatedError, InvalidParamInOverride
from algflow.algorithm.params import Param

logger = logging.getLogger('algflow.pipeline.param')


@dataclasses.dataclass
class ParamOverride:
    param_klass: Type[Param]
    data: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """
        This method searches for overriden data in the input dictionary and validates it.
        The validation step involves checking the use of aliases, renaming the keys if necessary,
        and checking for deprecated parameters. In case of hiearchical parameters, it also validates
        the nested parameters and checks for any unknown parameters.

        :param data: a dictionary containing specification for parameter overrides.
        :return: validated data which is a subset of data provided to validate function.
        """
        alg_name = self.param_klass.__algorithm__
        try:
            target_overrides, check_extra = self.data[alg_name], True
        except KeyError:
            target_overrides, check_extra = self.data, False

        self.data = {}
        overridden_keys = set()
        for k, v in self.param_klass.defined().items():
            try:
                self.data[k], alias_or_name = v.get_with_aliases(target_overrides)
                if alias_or_name != k:
                    logger.info(f'renaming param `{alias_or_name}` to {k} in algorithm {alg_name}')
                overridden_keys.add(alias_or_name)
                if v.deprecated:
                    raise ParamDeprecatedError(v, alg_name)
            except KeyError:
                pass  # parameter not overridden

        if check_extra:
            extra_keys = set(target_overrides.keys()).difference(overridden_keys)
            if extra_keys:
                raise InvalidParamInOverride(alg_name, extra_keys)
