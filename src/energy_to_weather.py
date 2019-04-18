#Solar: day’s conditions -  units of solar energy produced
#Wind: day’s conditions -  units of wind energy produced

#state representation
#[(solar, actual kWh?, predicted kWh?), (wind, kWh)...]

#reward function
#Given current state, action to be taken, next state, return value
#How close the kWh it generated (prediction) was to the actual data 

class ApproximateQAgent():  #(PacmanQAgent):
                """
                         ApproximateQLearningAgent

                         You should only have to overwrite getQValue
                         and update.  All other QLearningAgent functions
                         should work as is.
                """
                
                #def __init__(self, extractor='IdentityExtractor', **args):
                def __init__(self):
                                #self.featExtractor = util.lookup(extractor, globals())()
                                #self.featExtractor = list of features!!
                                #PacmanQAgent.__init__(self, **args)
                                #self.weights = util.Counter()
                                self.weights = [0 for _ in range(10)] #a list of the same length of features

                def getWeights(self):
                                return self.weights

                def getQValue(self, state, action):
                                """
                                        Should return Q(state,action) = w * featureVector
                                        where * is the dotProduct operator
                                """
                                "*** YOUR CODE HERE ***"
                                featureVector = self.featExtractor.getFeatures(state, action)
                                weight = self.getWeights()
                                result = weight * featureVector
                                return result

                def update(self, state, action, nextState, reward):
                                """
                                         Should update your weights based on transition
                                """
                                "*** YOUR CODE HERE ***"
                                featureVector = self.featExtractor.getFeatures(state,action)
                                difference = reward + (self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state,action)

                                for feature in featureVector:
                                        self.weights[feature] = self.getWeights()[feature] + (self.alpha * difference * featureVector[feature])

