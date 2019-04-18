from enum import Enum

class EnergySource(Enum):
    SOLAR = 1
    WIND = 2
    HYDRO = 3

class WeatherConditions(Enum):
    SUNLIGHT = 1
    WIND = 2
    PRECIPITATION = 3
