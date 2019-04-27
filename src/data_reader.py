import random

FORECAST_LIMIT = 10

#Class for holding Weather Data, windSpeed is in MPH and sunlight is a percentage in range [0, 1]
class WeatherData:
    windSpeed = 0
    sunlight = 0
    def __init__(self, _windSpeed, _sunlight):
        self.windSpeed = _windSpeed
        self.sunlight = _sunlight
    def __repr__(self):
        return (self.windSpeed, self.sunlight).__str__()
    def __str__(self):
        return (self.windSpeed, self.sunlight).__str__()

#Below are the public functions for a Reader
class Reader:
    def __init__(self):
        raise NotImplementedError("INTERFACE METHOD")
    #Returns True iff a call to getForecast will work as expected
    def canGetForecast(self):
        raise NotImplementedError("INTERFACE METHOD")
    #Returns a list (length = FORECAST_LIMIT) of WeatherData (assuming canGetForecast was true)
    def getForecast(self):
        raise NotImplementedError("INTERFACE METHOD")
    #Advances the time by one unit of time
    def advanceTime(self):
        raise NotImplementedError("INTERFACE METHOD")
        
#A class that just generates random weather forecast bound number of times (defaults to forever)
class RandomReader(Reader):
    time = 0
    data = []
    bound = -1
    def __init__(self, bound = -1):
        self.time = 0
        self.data = []
        self.bound = bound
        for i in range(FORECAST_LIMIT):
            self.data.append(self._genRandom())
    def canGetForecast(self):
        return self.bound != 0
    def getForecast(self):
        self.bound = self.bound - 1
        return self.data;
    def advanceTime(self):
        for i in range(FORECAST_LIMIT - 1):
            self.data[i] = self.data[i + 1]
        self.data[FORECAST_LIMIT - 1] = self._genRandom()
        self.time = self.time + 1
    def _genRandom(self):
        return WeatherData(random.random() * 20, random.random())


#Sample Code on a RandomReader
#rr = RandomReader(100)
#while rr.canGetForecast():
#    forecast = rr.getForecast()
#    print(forecast)
#    rr.advanceTime()
