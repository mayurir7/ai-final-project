from enum import Enum

class EnergySource(Enum):
    SOLAR = 0
    WIND = 1
    HYDRO = 2
    COAL = 3

class WeatherConditions(Enum):
    SUNLIGHT = 0
    WIND = 1
    PRECIPITATION = 2
