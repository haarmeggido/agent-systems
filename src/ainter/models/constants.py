from typing import Final

import numpy as np

# In seconds
DELTA_TIME: Final[np.float64] = np.float64(0.5)

# In meters
CELL_SIZE: Final[np.float64] = np.float64(0.25)

# In meters per seconds
SPEED_MAX: Final[np.float64] = np.float64(20)
SPEED_MIN: Final[np.float64] = np.float64(-10)

# In meters per seconds squared
ACCELERATION_MAX: Final[np.float64] = np.float64(2.5)
ACCELERATION_MIN: Final[np.float64] = np.float64(-1.5)
