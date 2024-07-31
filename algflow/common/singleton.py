import logging
from abc import ABCMeta


# class SingletonMetaClass(ABCMeta):
#     def __call__(cls, *args, **kwargs):
#         print(f'create {cls.__name__}', hasattr(cls, '_shared'))
#         if not hasattr(cls, '_shared'):
#             cls._shared = super().__call__(*args, **kwargs)
#         return cls._shared

logger = logging.getLogger('AlgFlowParam')


class SingletonMetaClass(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # logger.info(f'Singleton<{cls.__name__}> {cls._instances}')
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            logger.info(f'Singleton<{cls.__name__}>: create {hex(id(cls._instances[cls]))}')
        return cls._instances[cls]

    # @classmethod
    # def reset(mcs):
    #     logger.info('---Singleton Reset---')
    #     mcs._instances = {}


class Singleton(metaclass=SingletonMetaClass):
    pass