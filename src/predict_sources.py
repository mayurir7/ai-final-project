from data_reader import *
from weather_to_sources import *
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import os


class PredictSources():
#read in csv (use datareader), predict for each line, store prediction for each line

    def __init__(self, path_to_data=None):
        self.final_weights = self.getWeights()
        self.runner = Runner(1000, 500, 0.5, 0.1, 0.5)
        self.result = []

        if path_to_data is not None:
            self.runner.features.readData(path_to_data)
        
        self.prediction()

    def getWeights(self):
        input_dir = "../src"
        file = "final_weights.txt"
        input_file = os.path.join(input_dir, file)
        with open(input_file) as f:
            final_weights = pickle.load(f)
        return final_weights



    def prediction(self): 
        """
        Returns how much of each energy source we can use this hour.
        """

        #pass in energy_needed or else it'll just use ercot
        for weather_tuple in self.runner.features.raw_data:
            raw_data, features, action, energy_levels = self.runner.predict_iterate()
            self.result.append((raw_data, features, action, energy_levels))



if __name__ == '__main__':
    test = PredictSources()
