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
        print self.capacity
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
            print"-----------------"
            print "ITERATION: ", index
            raw_data, energy_gained, action, energy_levels, energy_needed = self.runner.predict_iterate()
            self.result.append((self.runner.features.raw_data[index], energy_gained, action, energy_levels, energy_needed))

if __name__ == '__main__':
    test = PredictSources(path_to_data = "../data/5months.txt", path_to_energy="../data/2018load.csv")
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

    print("total_renewables_used", total_renewables_used)
    print("total_energy_levels", total_energy_levels)
    print("total_energy_needed", total_energy_needed)
    print("total_coal_used", total_coal_used)

    print("renewable utilization", total_renewables_used / total_energy_levels)

    with open("predictions.txt", 'wb') as f:
        pickle.dump(test.result, f)

# april:
# ('total_renewables_used', 11188551.0)
# ('total_energy_levels', 35319030.79544331)
# ('total_energy_needed', 24830406.23999998)
# ('total_coal_used', 13641855.240000002)

#january
# ('total_renewables_used', 9456142.0)
# ('total_energy_levels', 147463509.14363718)
# ('total_energy_needed', 30366945.820000038)
# ('total_coal_used', 20910803.820000008)
# ('renewable utilization', 0.06412530160793355)



