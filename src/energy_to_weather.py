#Solar: day’s conditions -  units of solar energy produced
#Wind: day’s conditions -  units of wind energy produced

#state representation
#[(solar, kWh), (wind, kWh)...]

#reward function
#Given current state, action to be taken, next state, return value
#How close the kWh it generated was to the previous?

class ApproximateQAgent(PacmanQAgent):
                """
                         ApproximateQLearningAgent

                         You should only have to overwrite getQValue
                         and update.  All other QLearningAgent functions
                         should work as is.
                """
                def __init__(self, extractor='IdentityExtractor', **args):
                                self.featExtractor = util.lookup(extractor, globals())()
                                PacmanQAgent.__init__(self, **args)
                                self.weights = util.Counter()

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
                                result = weight * featureVector  #matrix multiply?
                                return result

#action class or enum

                def update(self, state, action, nextState, reward):
                                """
                                         Should update your weights based on transition
                                """
                                "*** YOUR CODE HERE ***"
                                featureVector = self.featExtractor.getFeatures(state,action)
                                difference = reward + (self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state,action)

                                for feature in featureVector:
                                        self.weights[feature] = self.getWeights()[feature] + (self.alpha * difference * featureVector[feature])

