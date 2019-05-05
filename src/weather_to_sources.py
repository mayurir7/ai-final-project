from data_reader import WeatherData
from data_reader import RandomReader
from data_reader import DataReader
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import os

class State():
    """
    State for the Q-learning situation
    """
    def __init__(self, day, hour):
        self.energy_levels = [0, 0, 0] #energy left, indexed by EnergySource enum
        self.day = day
        self.hour = hour
        FeatureExtractor().initializeState(self, RandomReader(365 * 5))

    def getWind(self):
        return self.energy_levels[EnergySource.WIND.value]
    
    def getSolar(self):
        return self.energy_levels[EnergySource.SOLAR.value]

    def getHydro(self):
        return self.energy_levels[EnergySource.HYDRO.value]


class FeatureExtractor():
    def __init__(self):
        self.raw_data = []  #holds the weather conditions
        self.features = []  #holds wind, solar, hydro energy in MW
        self.energy_needed = [] #read in from excel sheet/json -- this is the energy needed [MW] per hour
        self.readData()

    def readData(self):
        """
        Reads in weather data from a file and stores it
        """

        weather_reader = DataReader()
        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of tuples of (windSpeed, sunlight, energy_needed)
            for weather_tuple in forecast:
                #convert wind from miles/hour to meters/second
                weather_tuple.windSpeed = weather_tuple.windSpeed/2.237
            self.raw_data.append(forecast)
            weather_reader.advanceTime()


        #convert weather to power (mega watts)
        for day in self.raw_data:
            for weather_tuple in day:
                wind_power = self.calculate_wind_power(weather_tuple.windSpeed)
                solar_power = self.calculate_solar_power(weather_tuple.sunlight)
                hydro_power = self.calculate_hydro_power()
                self.features.append((wind_power, solar_power, hydro_power))
                self.energy_needed.append(weather_tuple.ERCOT)


    def calculate_wind_power(self, wind_speed):
        #returns wind power in mega watts

        air_density = 1 #could change but isn't that important
        area = 7853 #(max in texas onshore is 130 feet diameter, radius = 50ft, pi*r^2 == 7853)
        return (.5*air_density*area*(wind_speed ** 3)) / 1000000.0


    def calculate_solar_power(self, sun_hours):
        #returns solar power in mega watts

        fudge_factor = .75
        panel_wattage = 144000000 #http://www.ercot.com/gridinfo/resource (144 megawatts capactity in Travis county)
        return (panel_wattage*sun_hours*fudge_factor) / 1000000.0

    def calculate_hydro_power(self):
        #returns hydro power in mega watts

        efficiency = .8 #average hydroelectric plant efficiency
        water_density = 997
        flow_rate = 1 #may vary because of rain but usually doesn't
        gravity_acceleration = 9.8
        height_diff = 100.5 #austin's tom miller dam

        return (efficiency*water_density*flow_rate*gravity_acceleration*height_diff) / 1000000.0

    def getFeatures(self, state):
        """
        Returns the features for a given day and hour
        """
        index = ((state.day - 1) * 24) + (state.hour - 1)
        return self.features[index]

    def getEnergyNeeded(self, state):
        """
        Returns the energy needed for a given day and hour
        """
        index = ((state.day - 1) * 24) + (state.hour - 1)
        return self.energy_needed[index]

    def initializeState(self, state, weather_reader):
        """
        Given a reader, read in data for first 50 days and use to initialize
        """
        raw_data = []
        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of tuples
            for weather_tuple in forecast:
                #convert wind from miles/hour to meters/second
                weather_tuple.windSpeed = weather_tuple.windSpeed/2.237
            raw_data.append(forecast)
            weather_reader.advanceTime()

        # convert weather to power (mega watts)
        for day in raw_data:
            for weather_tuple in day:
                wind_power = self.calculate_wind_power(weather_tuple.windSpeed)
                solar_power = self.calculate_solar_power(weather_tuple.sunlight)
                hydro_power = self.calculate_hydro_power()
                state.energy_levels[EnergySource.WIND.value] += wind_power
                state.energy_levels[EnergySource.SOLAR.value] += solar_power
                state.energy_levels[EnergySource.HYDRO.value] += hydro_power


class ApproximateQLearner():
    """
    self.weights: list storing the weights, index matches up with features
    """

    def __init__(self, alpha, discount):
        self.weights = [random.random() for _ in range(len(WeatherConditions))]
        self.featExtractor = FeatureExtractor()
        self.discount = discount
        self.alpha = alpha
        self.legalActions = []

    def setLegalActions(self, actions):
        self.legalActions = actions

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
        Should return Q(state,action) = w * featureVector
        where * is the dotProduct operator
        """
        action = list(action)
        featureVector = self.featExtractor.getFeatures(state)
        weight = self.getWeights()
        result = 0.0
        for idx in range(len(featureVector)):
            result += (featureVector[idx] - action[idx]) * weight[idx]
        return result

    def computeValueFromQValues(self, state):
        """
        Returns Q value that comes from taking optimal action in this state
        """
        maxVal = 0
        for action in self.legalActions:
            temp = self.getQValue(state, action)
            if temp > maxVal:
                maxVal = temp
        return maxVal

    def update(self, state, action, nextState, reward):
        """
        Should update your weights based on transition
        """
        featureVector = self.featExtractor.getFeatures(state)
        difference = reward + (self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state, action)
        # print "Q VALUE: ", self.getQValue(state, action)
        # print "VALUE FROM Q VALUE: ", self.computeValueFromQValues(nextState)
        for idx in range(len(featureVector)):
            self.weights[idx] = self.weights[idx] + (self.alpha * difference * featureVector[idx])
        
        # normalize weights because everything is a hack
        self.weights = [float(i) / sum(self.weights) for i in self.weights]

class Runner():
    def __init__(self, iterations, max_energy_needed, epsilon, alpha, discount):
        self.epsilon = epsilon
        self.learner = ApproximateQLearner(alpha, discount)
        self.features = FeatureExtractor()
        self.iterations = iterations
        self.state = State(0, 0)
        self.action_space = self.generateLegalActions(max_energy_needed)

    def generateLegalActions(self, max_energy_needed):
        """
        Returns an array of actions for the largest energy needed
        """
        incr = max_energy_needed / 500 if max_energy_needed > 500 else 1
        result = [item for item in itertools.product(range(0, max_energy_needed, incr), repeat=3)]
        return result

    def getLegalActions(self, energy_needed):
        actions = []
        for (w, s, h) in self.action_space:
            if s + w + h <= energy_needed and self.state.getWind() >= w and self.state.getSolar() >= s and self.state.getHydro() >= h:
                actions.append((w, s, h))
        return actions

    def getAction(self, state, actions, epsilon):
        if random.random() <= epsilon:
            # choose random action
            index = (int)(random.random() * len(actions))
            return actions[index]
        else:
            # choose optimal action
            bestAction = None
            bestQVal = None
            for action in actions:
                qval = self.learner.getQValue(state, action)
                if bestQVal == None:
                    bestAction = action
                    bestQVal = qval
                elif qval >= bestQVal:
                    bestAction = action
                    bestQVal = qval
            return bestAction

    def iterate(self):
        # get energy needed for that day/hour
        energy_needed = self.features.getEnergyNeeded(self.state)
        # get legal actions and set in Q-learner
        legalActions = self.getLegalActions(energy_needed)
        self.learner.setLegalActions(legalActions)
        # take optimal action
        action = self.getAction(self.state, legalActions, self.epsilon)
        # calculate next state
        nextState = self.state
        if nextState.hour > 24:
            nextState.day += 1
            nextState.hour = 1
        else:
            nextState.hour += 1
        
        for idx in range(len(nextState.energy_levels)):
            nextState.energy_levels[idx] = nextState.energy_levels[idx] - list(action)[idx] + self.features.getFeatures(self.state)[idx]
        
        # learn from it
        reward = self.calculateReward(self.state, action)
        self.learner.update(self.state, action, nextState, reward)
        self.state = nextState
        print "ACTION: " , action
        print "WEIGHTS: ", self.learner.weights
        print "FEATURES: ", self.features.getFeatures(self.state)

    def calculateReward(self, state, action):
        """
        Calculates reward for given state based on how much coal used
        """

        renewables = 0
        for power in action:
            renewables = renewables + power

        coal_used = self.features.getEnergyNeeded(state) - renewables

        # return 1 / coal_used
        return renewables

    def run(self):
        for idx in range(self.iterations):
            self.iterate()
            print "ENERGY LEVELS: ", self.state.energy_levels # logging



if __name__ == '__main__':
    # iterations, max energy, epsilon, alpha, discount
    test = Runner(1000, 70000, 0.5, 0.01, 0.5)
    print "STARTING WEIGHTS: " , test.learner.weights
    print "STARTING ENERGY LEVELS: ", test.state.energy_levels
    test.run()


    #pipe final weights to a file
    output_dir = "../src"
    output_filename = 'final_weights.txt'
    output_file = os.path.join(output_dir, output_filename)
    with open(output_file, 'wb') as f:
        pickle.dump(test.learner.weights, f)
        
