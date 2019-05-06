from data_reader import *
from weather_to_sources import *
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import os


class PredictSources():
    def __init__(self):
        self.final_weights = self.getWeights()
        self.runner = Runner(1000, 500, 0.5, 0.01, 0.5)
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
        Returns which energy source will be used for this hour.

        return how much of this energy source we can use???
        """

        current_features = self.runner.features.getFeatures(self.runner.state)

        prediction = [0 for i in range(3)]

        for i in range(len(self.final_weights)):
            prediction[i] = self.final_weights[i]*current_features[i]

        
        source = prediction.index(max(prediction))
        return EnergySource(source)

if __name__ == '__main__':
    test = PredictSources()