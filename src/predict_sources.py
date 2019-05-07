from data_reader import *
from weather_to_sources import *
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import os
import sys

class PredictSources():
    """
    Class that takes in a client's weather conditions and predicts the optimal
    mix of renewable energy sources to utilize per hour
    """

    def __init__(self, path_to_data=None, path_to_energy=None):
        self.final_weights = self.getWeights()
        self.runner = Runner(0, 500, 0.5, 0.1, 0.5, path_to_data, path_to_energy)
        self.startingEnergyLevel = self.runner.state.energy_levels
        self.result = []

        self.prediction()

    def getWeights(self):
        """
        Read in final weights learned from training
        """
        input_dir = "../src"
        if "ui" in os.getcwd():
            input_dir = "../"
        file = "final_weights.txt"
        input_file = os.path.join(input_dir, file)
        with open(input_file) as f:
            final_weights = pickle.load(f)
        return final_weights



    def prediction(self): 
        """
        Returns how much of each energy source we can use this hour.
        """

        for weather_tuple in self.runner.features.raw_data:
            raw_data, features, action, energy_levels = self.runner.predict_iterate()
            self.result.append((raw_data, features, action, energy_levels))



if __name__ == '__main__':
    test = PredictSources(path_to_data = "../data/10monthsV2.txt")
