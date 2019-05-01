#Solar: day’s conditions -  units of solar energy produced
#Wind: day’s conditions -  units of wind energy produced

#state representation
#[[solar level, wind level, hydro level], day, hour]

#action representation
#int matching up with action enum

#reward function
#Given current state, action to be taken, next state, return value
#How close the kWh it generated (prediction) was to the actual data 

from energy_to_sources import State
from energy_to_sources import FeatureExtractor
from enums import EnergySource

class ApproximateQAgent():  #(PacmanQAgent):
    def __init__(self):
        self.weights = [0 for _ in range(len(WeatherConditions))]
        self.featExtractor = FeatureExtractor()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
    """
        Should return Q(state,action) = w * featureVector
        where * is the dotProduct operator
    """
        featureVector = self.featExtractor.getFeatures(state, action)
        weight = self.getWeights()
        result = weight * featureVector
        return result

    def computeValueFromQValues(self, state):
    """
        Returns Q value that comes from taking optimal action
        in this state
    """
        maxVal = 0
        for action in range(EnergySource):
            temp = getQValue(state, action)
            if temp > maxVal:
                maxVal = temp
        return maxVal

    def update(self, state, action, nextState, reward):
    """
        Should update your weights based on transition
    """
        featureVector = self.featExtractor.getFeatures(state,action)
        difference = reward + (self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state,action)

        for feature in featureVector:
            self.weights[feature] = self.getWeights()[feature] + (self.alpha * difference * featureVector[feature])
