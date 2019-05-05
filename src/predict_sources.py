from data_reader import WeatherData
from data_reader import RandomReader
from weather_to_sources import FeatureExtractor
from weather_to_sources import State
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import os


class PredictSources():
    def __init__(self):
        self.final_weights = self.getWeights()
        self.raw_data = []
        self.featExtractor = FeatureExtractor()
        self.features = []
        self.energy_needed = []
        self.energy_levels = [] #add this!!
        self.getData()


    def getWeights(self):
        input_dir = "../src"
        file = "final_weights.txt"
        input_file = os.path.join(input_dir, file)
        with open(input_file) as f:
            final_weights = pickle.load(f)
        return final_weights


    def getData(self):
        #get new data, not training data
        weather_reader = RandomReader(365) #should/can we read in all days at once?
        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of tuples
            for weather_tuple in forecast:
                #convert wind from miles/hour to meters/second
                weather_tuple.windSpeed = weather_tuple.windSpeed/2.237
            self.raw_data.append(forecast)
            weather_reader.advanceTime()


        #convert weather conditions to power (mega watts)
        for day in self.raw_data:
            for weather_tuple in day:
                wind_power = self.featExtractor.calculate_wind_power(weather_tuple.windSpeed)
                solar_power = self.featExtractor.calculate_solar_power(weather_tuple.sunlight)
                hydro_power = self.featExtractor.calculate_hydro_power()
                self.features.append((wind_power, solar_power, hydro_power))


        #read in self.energy_needed from csv!!!
        for idx in range(0, 365 * 24): #TODO: make this actually read in data
            self.energy_needed.append(50000)

    # def getFeatures(self, state):
    #     """
    #     Returns the features for a given day and hour
    #     """
    #     index = ((state.day - 1) * 24) + (state.hour - 1)
    #     return self.features[index]

    # def getEnergyNeeded(self, state):
    #     """
    #     Returns the energy needed for a given day and hour
    #     """
    #     index = ((state.day - 1) * 24) + (state.hour - 1)
    #     return self.energy_needed[index]


    def prediction(self):
        #prediction = weights * features




if __name__ == '__main__':
    test = PredictSources()