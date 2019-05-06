from data_reader import *
from weather_to_sources import *
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import os


class PredictSources():
#read in csv, predict for each line, store prediction for each line

    def __init__(self, path_to_csv=None):
        self.final_weights = self.getWeights()
        self.runner = Runner(1000, 500, 0.5, 0.01, 0.5)
        if path_to_csv is not None:
            self.loadCSV(path_to_csv)
        # self.prediction()


    def getWeights(self):
        input_dir = "../src"
        file = "final_weights.txt"
        input_file = os.path.join(input_dir, file)
        with open(input_file) as f:
            final_weights = pickle.load(f)
        return final_weights

    def loadCSV(self, path_to_csv):
        with open(path_to_csv) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                weather_tuple = (row,)
                self.raw_data.append(weather_tuple)
                prediction(weather_tuple)





    def prediction(self, weather_tuple): #pass in energy_needed, legalActions?, energy_levels? (should this be 0,0,0 at start or initialized?), 
        """
        Returns how much of each energy source we can use this hour.
        """

        # current_raw_data is given from the call from loadCSV?

        current_raw_data, features, action, energy_levels = self.runner.predict_iterate()
        return action




if __name__ == '__main__':
    test = PredictSources()
