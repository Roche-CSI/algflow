from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar, Tuple, Dict, Any, List, Optional, Self
from traits.trait_type import TraitType
from numpy import typing as npt
import numpy as np
from rich import print

TYPE_MAPPING = {
    'Float': np.float64,
    'Int': np.int64,
}


@dataclass
class DataVariable:
    name: str
    type: str   # underlying typing system name ( Array, Float, Integer etc. )
    dtype: Optional[npt.DTypeLike] = None # Equivalent Numpy Data Type
    shape: Optional[Tuple[int, ...]] = None  # Numpy compatible Shape if needed

    def set_numpy_props(self, trait: TraitType):
        #print(f'setting numpy props on {self.name} {trait} {self}')
        if trait._metadata.get('array', False):
            self.dtype = trait.dtype
            self.shape = trait.shape
        elif self.type == 'Float':
            self.dtype = np.float64
        else:
            self.dtype = TYPE_MAPPING.get(self.name)

class DataLayout(Enum):
    NORMAL = 0          # Normal input (e.g. numpy array, pandas dataframe, scalar etc.)
    CHUNKED = 1         # Very large input which can be chunked (e.g. large numpy array,
    # large pandas dataframe etc.)
    STREAM = 2          # Stream of data (e.g. video stream, audio stream etc., )


# TDataDescriptor = TypeVar("TDataDescriptor", bound="AlgFlowDataDescriptor")

@dataclass
class AlgFlowDataDescriptor(DataVariable):
    layout: DataLayout = DataLayout.NORMAL
    parametrized: bool = False
    path: Optional[str] = None
    query_params: List[str] = field(default_factory=lambda: [])
    meta: Dict[str, Any] = field(default_factory=lambda: {})

    @classmethod
    def read_descriptors(cls, h5) -> Dict[str, Self]:
        pass

    @classmethod
    def from_variable(cls, var: DataVariable) -> Self:
        return cls(var.name, var.type, var.dtype, var.shape)
