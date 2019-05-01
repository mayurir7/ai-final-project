from enum import Enum

class EnergySource(Enum):
    WIND = 0
    SOLAR = 1
    HYDRO = 2

class WeatherConditions(Enum):
    SUNLIGHT = 0
    WIND = 1
    PRECIPITATION = 2
