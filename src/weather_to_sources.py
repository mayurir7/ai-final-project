from data_reader import WeatherData
from data_reader import RandomReader

class State():
    """
    State for the Q-learning situation
    """
    def __init__(self, day, hour):
        self.energy_levels = [] #energy left, indexed by EnergySource enum
        self.day = day
        self.hour = hour

    def updateEnergy(self, energy_used):
        """
        Pass in array of amounts of energy consumed, indexed by EnergySource
        """
        for index in range(len(energy_levels)):
            energy_levels[index] = energy_levels[index] - energy_used[index]

class FeatureExtractor():
    def __init__(self):
        self.raw_data = []
        self.readData()

    def readData(self):
        """
        Reads in weather data from a file and stores it (in self.raw_data)
        """

        #read in weather data from csv/call scraper

        #read in all days at once?
        weather_reader = RandomReader(365) #365 days, with 24 tuples of (wind,sun) in each day?
        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of tuples
            for weather_tuple in forecast:
                #convert wind from miles/hour to meters/second
                weather_tuple.windSpeed = weather_tuple.windSpeed/2.237
            self.raw_data.append(forecast)
            weather_reader.advanceTime()
        

        #convert weather to power (watts)
        #go through self.data and calculate power for the hour
        hourly_power = []
        for day in self.raw_data:
            for weather_tuple in day:
                wind_power = self.calculate_wind_power(weather_tuple.windSpeed)
                solar_power = self.calculate_solar_power(weather_tuple.sunlight)
                hydro_power = self.calculate_hydro_power()
                hourly_power.append((wind_power, solar_power, hydro_power))

        self.features = hourly_power

    def calculate_wind_power(self, wind_speed):
        #returns wind power in watts

        air_density = 1 #could change but isn't that important
        area = 7853 #(max in texas onshore is 130 feet diameter, radius = 50ft, pi*r^2 == 7853)
        return .5*air_density*area*(wind_speed ** 3)


    def calculate_solar_power(self, sun_hours):
        #returns solar power in watts
        
        fudge_factor = .75
        panel_wattage = 144000000 #http://www.ercot.com/gridinfo/resource (144 megawatts capactity in Travis county)
        return panel_wattage*sun_hours*fudge_factor

    def calculate_hydro_power(self):
        #returns hydro power in watts
        
        efficiency = .8 #average hydroelectric plant efficiency
        water_density = 997
        flow_rate = 1 #may vary because of rain but usually doesn't
        gravity_acceleration = 9.8
        height_diff = 100.5 #austin's tom miller dam

        return efficiency*water_density*flow_rate*gravity_acceleration*height_diff

    def getFeatures(self, state):
        """
        Returns the features for a given day and hour
        """
        index = ((state.day - 1) * 24) + (state.hour - 1)
        return self.features[index]

if __name__ == '__main__':
    test = FeatureExtractor()

