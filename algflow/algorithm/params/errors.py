from typing import Set
from .param_variable import ParamVariable
from ..types import AlgName


class ParamSourceError(Exception):
    def __init__(self, alg_name, ref_p: ParamVariable):
        msg = f"parameter `{alg_name}.{ref_p.name}` references the algorithm `{ref_p.ref}` which is not defined"
        super().__init__(msg)


class ReferencedParamTypeError(Exception):
    def __init__(self, alg_name: str, ref_p: ParamVariable, def_p: ParamVariable):
        msg = f"expecting `{def_p.type}` for parameter `{ref_p.name}` " \
              f"referenced in class `{alg_name}` but got `{ref_p.type}` "
        super().__init__(msg)


class ReferencedParamNotDefined(Exception):
    def __init__(self, alg_name: str, param: ParamVariable):
        msg = f"parameter `{param.name}` for algorithm `{alg_name}` not defined in referenced algorithm/param class `{param.ref}`"
        super().__init__(msg)


class ParamRegistrationError(Exception):
    pass


class ParamSetAlreadyRegistered(Exception):
    def __init__(self, cname: str):
        msg = f"param set `{cname}` is already registered."
        super().__init__(msg)


class ReferencedParamSetNotFound(Exception):
    def __init__(self, alg_name: AlgName):
        msg = (f'The source `{alg_name}` is not initialized.The referenced param classes need to '
               f'be instantiated first.')
        super().__init__(msg)

class InvalidParamInOverride(Exception):
    def __init__(self, alg_name: AlgName, invalid_params: Set[str]):
        if len(invalid_params) > 1:
            msg = f"The parameters `{','.join(invalid_params)}` are"
        else:
            msg = f"The parameter `{','.join(invalid_params)}` is"
        msg += f" not defined in algorithm `{alg_name}`. Please check your parameter overrides."
        super().__init__(msg)


class InvalidAlgInParamOverride(Exception):
    def __init__(self, alg_name: str):
        msg = f"The algorithm `{alg_name}` specified in parameter overrides is not found."
        super().__init__(msg)


class ParamDeprecatedError(Exception):
    def __init__(self, param: ParamVariable, alg_name: str):
        msg = f"The parameter `{param.name}`"
        if param.aliases:
            msg += f" or `{','.join(param.aliases)}`"
        msg += f" defined in algorithm `{alg_name}` is deprecated. Please remove from your parameter specification. "
        super().__init__(msg)
