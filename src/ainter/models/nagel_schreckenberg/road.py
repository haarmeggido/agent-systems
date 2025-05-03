from dataclasses import dataclass
from typing import Self

import numpy as np

from ainter.models.nagel_schreckenberg.units import discretize_length


@dataclass(slots=True, frozen=True)
class Road:
    grid: np.ndarray
    lanes_forward: int
    lanes_backward: int

    @classmethod
    def from_length(cls, length: np.float64, lanes_forward: int, lanes_backward: int) -> Self:
        cells_num = discretize_length(length.astype(np.float32))

        return cls(grid=np.zeros(shape=(cells_num, lanes_forward + lanes_backward), dtype=np.uint8),
                   lanes_forward=lanes_forward,
                   lanes_backward=lanes_backward)
