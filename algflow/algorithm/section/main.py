from types import new_class


class MixinTypeError(Exception):
    def __init__(self, section, mixin_class):
        super().__init__(f'{mixin_class.__name__} mixin passed is expected to be a subclass '
                         f'of {section.__name__}')


def extract_class_spec(klass):
    return {name: value for (name, value) in
            vars(klass).items() if not name.startswith('__')} if klass else {}


class Section(object):
    def __init__(self, klass, mixnis_allowed=False):
        self.name = klass.__name__
        self.klass = klass
        self.mixins_allowed = mixnis_allowed

    def infer_hier_bases(self, alg_bases):
        hier = []
        for base in alg_bases:
            base = getattr(base, self.name)
            if base:
                hier.append(base)
        return hier

    def extract_mixnis(self, section_class):
        if section_class is None:
            return []

        mixins = vars(section_class).get("__mixins__", [])
        if mixins and not self.mixins_allowed:
            raise ValueError('Mixins Not Allowed')

        # Validating the type of the Mixin.
        for klass in mixins:
            if not issubclass(klass, self.klass):
                raise MixinTypeError(section_class, klass)
        return mixins

    def __call__(self, alg_name: str, alg_bases: tuple, class_dict: dict):
        """
        Algflow supports nested classes 'Input', 'Output' and 'Param' to specify typed io, outputs and parameters.
        These nested classes are specified in bare format without any base classes or metaclasses constraints.
        In order to implement type checking on Input, Output and Parameter classes are re-created using corresponding
        base classes. Suppose we have an algorithm A3 derived from A2 which in turns derived from A1 i.e
            A3 <- A2 <- A1
        Then this routine establishes following hierarchy for the Section
            A3.[Section] <- A2.[Section] <- A1.[Section] <- [SectionBase]
        Continuing the example for A3 Output section this would look like
            ORIGINAL:                       DERIVED:
            class A3(A2):                   class A3(A2):
                class Input:                   class Input(A2.Input):
                    ...                             ...
                    ...                             ...

            class A2(A1):                   class A2(A1):
                class Output:                   class Output(A1.Output):
                    ...                             ...
                    ...                             ...

            lass A1(Algorithm):             class A1(Algorithm):
                class Output:                   class Output(algflow.inout.Output):
                    ...                             ...
                    ...                             ...

        This routine implements this mixin behaviour.

        :param alg_name: str. The name of the algorithm where the section class is defined
        :param alg_bases: Tuple[Type[Algorithm]]. The base classes of algorithm to define the implicit and direct hierarchy
                            between section
        :param class_dict: Dict. The section class member dict.
        :return:
        """
        section_class = class_dict.get(self.name, None)

        # automatically create inheritance between sections of the base classes
        # b1 = self.extract_mixnis(section_class)
        # b2 = self.infer_hier_bases(alg_bases)
        section_bases = self.extract_mixnis(section_class) + self.infer_hier_bases(alg_bases)
        if not section_bases:
            section_bases = [self.klass]

        def exec_body(ns):
            ns['_parent'] = alg_name
            param_props = extract_class_spec(section_class)
            ns.update(param_props)

        # print('DERIVING PARAM CLASS:', alg_name)
        klass = new_class(f"{self.name}<{alg_name}>", tuple(section_bases), exec_body=exec_body)
        # print('ParamClass:', ParamClass.__dict__)
        return klass
