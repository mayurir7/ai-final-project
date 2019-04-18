class FeatureExtractor():
    def __init__(self, filename):
        self.data = []
        readData(filename)

    def readData(self, filename):
        """
        Reads in weather data from a file and stores it somehow (in self.data?)
        """

        print("done")

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
        self.weights = [0 for _ in range(len(WeatherConditions))]
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
