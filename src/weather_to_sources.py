class State():
    """
    State for the Q-learning situation
    """
    def __init__(self):
        self.energy_levels = [] # energy left, indexed by EnergySource enum
        self.weather = []

    def updateEnergy(self, energy_used):
        """
        Pass in array of amounts of energy consumed, indexed by EnergySource
        """
        for index in range(len(energy_levels)):
            energy_levels[index] = energy_levels[index] - energy_used[index]

class FeatureExtractor():
    def __init__(self, filename):
        self.data = []
        readData(filename)

    def readData(self, filename):
        """
        Reads in weather data from a file and stores it somehow
        """
        print "done"

    def next(self):
        """
        Returns the features for the next hour timeslot
        """
        return None


class ApproximateQLearner():
    """
    self.weights: list storing the weights, index matches up with features
    """
    
    def __init__(self):
        self.weights = []
        self.featExtractor = FeatureExtractor()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
        Should return Q(state,action) = w * featureVector
        where * is the dotProduct operator
        """
        featureVector = getFeatures()
        weight = self.getWeights()
        result = weight * featureVector  #matrix multiply?
        return result

    def update(self, state, action, nextState, reward):
        """
        Should update your weights based on transition
        """
        featureVector = self.featExtractor.getFeatures(state,action)
        difference = reward + (self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state,action)
        for feature in featureVector:
            self.weights[feature] = self.getWeights()[feature] + (self.alpha * difference * featureVector[feature])

    def calculateReward(self, state):
        """
        Calculates the reward for the given state
        Reward should be a mix of balanced-ness of energy levels + 
        """
