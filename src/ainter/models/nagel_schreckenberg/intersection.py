from dataclasses import dataclass
from typing import Self

import numpy as np


@dataclass(slots=True, frozen=True)
class Intersection:
    grid: np.array

    @classmethod
    def from_grid(cls) -> Self:
        return cls(np.zeros(shape=(10, 10), dtype=np.uint8))
