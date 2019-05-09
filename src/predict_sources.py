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
        self.capacity = list(self.runner.features.capacity)
        self.result = []

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
    test = PredictSources(path_to_data = "../data/april.txt", path_to_energy="../data/2018load.csv")
    test.prediction()
    total_energy_levels = 0.0
    total_renewables_used = 0.0
    total_energy_needed = 0.0
    total_coal_used = 0.0
    for tuple in test.result:
        actions = tuple[2]
        energy_levels = tuple[3]
        energy_needed = tuple[4]
        renewables_used_per_hour = 0.0
        
        for action in actions:
            total_renewables_used += action
            renewables_used_per_hour += action
        total_coal_used += energy_needed - renewables_used_per_hour
        for energy in energy_levels:
            total_energy_levels += energy
        total_energy_needed += energy_needed
        print actions, energy_levels, energy_needed



