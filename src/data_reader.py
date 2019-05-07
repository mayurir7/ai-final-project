import random
import math

FORECAST_LIMIT = 24
daysinmonth = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#Class for holding Weather Data, windSpeed is in MPH and sunlight is a percentage in range [0, 1]
class WeatherData:
    windSpeed = 0
    sunlight = 0
    ERCOT = 0
    month = 0
    day = 0
    year = 0
    hour = 0
    minute = 0
    def __init__(self, _windSpeed, _sunlight, _ERCOT, _sun, _temp, _month, _day, _year, _hour, _minute):
        self.windSpeed = _windSpeed / 2.237 #convert from mph to meters per second
        self.sunlight = _sunlight
        self.ERCOT = _ERCOT
        self.sunForecast = _sun
        self.temperature = _temp
        self.month = _month
        self.day = _day
        self.year = _year
        self.hour = _hour
        self.minute = _minute
    def __repr__(self):
        return (self.windSpeed, self.sunlight, self.ERCOT, self.sunForecast, self.temperature, self.month, self.day, self.year, self.hour, self.minute).__str__()
    def __str__(self):
        return (self.windSpeed, self.sunlight, self.ERCOT, self.sunForecast, self.temperature, self.month, self.day, self.year, self.hour, self.minute).__str__()

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
        return WeatherData(random.random() * 20, random.random(), 25000 + random.random() * 25000, .5, 70, -1, -1, -1, -1, -1)

class DataReader(Reader):
    time = 0
    data = []
    def canGetForecast(self):
        return len(self.data) >= FORECAST_LIMIT + self.time
    def getForecast(self):
        return self.data[self.time : (self.time + FORECAST_LIMIT)]
    def advanceTime(self):
        self.time = self.time + 1
    def __init__(self, path_to_data="../data/10monthsV2.txt", path_to_energy="../data/2018load.csv"):
        self.time = 0
        self.data = []
        emap = dict()
        f = open(path_to_energy)
        skip = True
        for row in f:
            if skip:
                skip = False
                continue
            data = row.split(",")
            date, time = data[0].strip().split(" ")
            month, day, year = map(int, date.split("/"))
            hour = int(time.split(":")[0])
            if month == 11 and day >= 2:
                break
            ercot = float(data[9].strip())
            emap[(month, day, year, hour)] = ercot
        f.close()
        f = open(path_to_data)
        #month = 1
        #day = 1
        #year = 2018
        lasthour = 0
        conds = set()
        for row in f:
            month, day, year, time, temp, windspeed, cond = row.split(",")
            month = int(month.strip())
            day = int(day.strip())
            year = int(year.strip())
            time = time.strip()
            hour, minute = time.split(":")
            hour = int(hour)
            minute = int(minute)
            temp = int(temp.strip())
            windspeed = int(windspeed.strip())
            cond = cond.strip()
            suntime = math.sqrt(max(0, math.sin((3.141592 / 12) * hour)))
            suncond = 1
            if(cond == "Fair"):
                suncond = 1
            elif(cond == "Fair / Windy"):
                suncond = 1
            elif(cond == "Light Drizzle"):
                sundcond = .8
            elif(cond == "Mostly Cloudy"):
                suncond = .7
            elif(cond == "Thunder"):
                suncond = .5
            elif(cond == "T-Storm"):
                suncond = .5
            elif(cond == "Light Rain / Windy"):
                suncond = .9
            elif(cond == "Haze"):
                suncond = .9
            elif(cond == "Fog"):
                suncond = .8
            elif(cond == "Mostly Cloudy / Windy"):
                suncond = .7
            elif(cond == "Heavy T-Storm / Windy"):
                suncond = .3
            elif(cond == "Squalls / Windy"):
                suncond = .7
            elif(cond == "Thunder in the Vicinity"):
                suncond = 1
            elif(cond == "Light Rain"):
                suncond = .9
            elif(cond == "Rain"):
                suncond = .7
            elif(cond == "Patches of Fog"):
                suncond = .9
            elif(cond == "T-Storm / Windy"):
                suncond = .5
            elif(cond == "N/A"):
                suncond = 1
            elif(cond == "Cloudy / Windy"):
                suncond = .8
            elif(cond == "Partly Cloudy / Windy"):
                suncond = .9
            elif(cond == "Heavy Rain"):
                suncond = .5
            elif(cond == "Cloudy"):
                suncond = .8
            elif(cond == "Squalls"):
                suncond = .7
            elif(cond == "Rain / Windy"):
                suncond = .7
            elif(cond == "Light Drizzle / Windy"):
                suncond = .95
            elif(cond == "Light Rain with Thunder"):
                suncond = .5
            elif(cond == "Heavy T-Storm"):
                suncond = .3
            elif(cond == "Heavy Rain / Windy"):
                suncond = .5
            elif(cond == "Partly Cloudy"):
                suncond = .9
            elif(cond == "Mist"):
                suncond = .8
            elif(cond == "Haze / Windy"):
                suncond = .8
            #else:
            #    conds.add(cond)
            if(hour == 0 and lasthour != 0):
                day = day + 1
                if(day > daysinmonth[month]):
                    day = 1
                    month = month + 1
            if(month == 3 and day == 11 and year == 2018 and (hour + 1) == 3):
                #DST
                continue
            wd = WeatherData(windspeed, suntime * suncond, emap[(month, day, year, hour + 1)], cond, temp, month, day, year, hour, minute)
            if(hour == lasthour and len(self.data) > 0):
                self.data[len(self.data) - 1] = wd
            else:
                self.data.append(wd)
            lasthour = hour
        f.close()


#Sample Code on a RandomReader
#rr = RandomReader(100)
#while rr.canGetForecast():
#    forecast = rr.getForecast()
#    print(forecast)
#    rr.advanceTime()

#Sample Code on a DataReader
#dr = DataReader()
#while dr.canGetForecast():
#    forecast = dr.getForecast()
#    print(forecast)
#    dr.advanceTime()
