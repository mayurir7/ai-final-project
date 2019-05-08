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
        self.runner = Runner(0, 70000, 0, 0.1, 0.5, path_to_data, path_to_energy, debug=True)
        self.capacity = list(self.runner.features.capacity) #capacity
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

        for index in range(len(self.runner.features.raw_data) - 1):
            raw_data, energy_gained, action, energy_levels, energy_needed = self.runner.predict_iterate()
            self.result.append((self.runner.features.raw_data[index], energy_gained, action, energy_levels, energy_needed))

if __name__ == '__main__':
    test = PredictSources(path_to_data = "../data/3days.txt", path_to_energy="../data/2018load.csv")
    for tuple in test.result:
        print tuple[2] , tuple[3] , tuple[4]
