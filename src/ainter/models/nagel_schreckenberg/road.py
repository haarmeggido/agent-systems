from dataclasses import dataclass
from typing import Self

import numpy as np

import ainter.models.constants


@dataclass(slots=True, frozen=True)
class Road:
    grid: np.ndarray
    lanes_forward: int
    lanes_backward: int

    @classmethod
    def from_length(cls, length: np.float64, lanes_forward: int, lanes_backward: int) -> Self:
        cells_num = np.floor(length / ainter.models.constants.CELL_SIZE).astype(int)

        return cls(grid=np.zeros(shape=(cells_num, lanes_forward + lanes_backward), dtype=np.uint8),
                   lanes_forward=lanes_forward,
                   lanes_backward=lanes_backward)