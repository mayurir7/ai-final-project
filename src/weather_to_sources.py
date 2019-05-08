from data_reader import WeatherData
from data_reader import RandomReader
from data_reader import DataReader
from enums import EnergySource, WeatherConditions
import itertools
import random
import pickle
import csv
import os

class State():
    """
    State for the Q-learning situation
    """
    def __init__(self, day, hour, featureExtractor):
        self.energy_levels = [0, 0, 0] #energy left, indexed by EnergySource enum
        self.day = day
        self.hour = hour
        featureExtractor.initializeState(self, RandomReader(24 * 24))

    def getWind(self):
        return self.energy_levels[EnergySource.WIND.value]
    
    def getSolar(self):
        return self.energy_levels[EnergySource.SOLAR.value]

    def getHydro(self):
        return self.energy_levels[EnergySource.HYDRO.value]


class FeatureExtractor():
    """
    Converts weather conditions to power
    """
    def __init__(self, path_to_data=None, path_to_energy=None):
        self.raw_data = []  #holds the weather conditions per hour
        self.features = []  #holds (wind, solar, hydro) in MW per day
        self.energy_needed = [] #holds energy needed in MW per hour
        self.energy_gained = [] # holds energy gained per hour
        self.capacity = [0.0,0.0,0.0]
        self.readData(path_to_data, path_to_energy)

    def readData(self, path_to_data, path_to_energy):
        """
        Reads in weather data from a file and stores it
        """

        if path_to_data == None:
            weather_reader = RandomReader(365 * 24)
        else:
            weather_reader = DataReader(path_to_data, path_to_energy)

        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of 24 tuples of (windSpeed, sunlight, energy_needed)
            # store raw numbers
            self.raw_data.append(forecast[0])
            self.energy_needed.append(forecast[0].ERCOT)
            self.energy_gained.append((self.calculate_wind_power(forecast[0].windSpeed), self.calculate_solar_power(forecast[0].sunlight), self.calculate_hydro_power()))
            # calculate features
            wind_power = 0.0
            solar_power = 0.0
            hydro_power = 0.0
            for weather_tuple in forecast:
                #convert weather to power
                wind_power += self.calculate_wind_power(weather_tuple.windSpeed)
                solar_power += self.calculate_solar_power(weather_tuple.sunlight)
                hydro_power += self.calculate_hydro_power()
            self.features.append((wind_power, solar_power, hydro_power))
            weather_reader.advanceTime()

    def calculate_wind_power(self, wind_speed):
        """
        Returns wind power in mega watts
        """

        air_density = 1 #could change but isn't that important
        area = 7853 #(max in texas onshore is 130 feet diameter, radius = 50ft, pi*r^2 == 7853)
        num_turbines = 13000 # there are 13000 wind turbines in Texas
        return (.5*air_density*area*(wind_speed ** 3)) / 1000000.0 * num_turbines


    def calculate_solar_power(self, sun_hours):
        """
        Returns solar power in mega watts
        """

        fudge_factor = .75
        panel_wattage = 144000000 #http://www.ercot.com/gridinfo/resource (144 megawatts capacity in Travis county)
        return (panel_wattage*sun_hours*fudge_factor) / 1000000.0

    def calculate_hydro_power(self):
        """
        Returns hydro power in mega watts
        """

        efficiency = .8 #average hydroelectric plant efficiency
        water_density = 997
        flow_rate = 1 #may vary because of rain but usually doesn't
        gravity_acceleration = 9.8
        height_diff = 100.5 #austin's tom miller dam
        num_dams = 12

        return (efficiency*water_density*flow_rate*gravity_acceleration*height_diff) / 1000000.0 * num_dams

    def getFeatures(self, state):
        """
        Returns the features for a given day and hour
        """
        index = ((state.day) * 24) + (state.hour)
        return self.features[index]

    def getEnergyNeeded(self, state):
        """
        Returns the energy needed for a given day and hour
        """
        index = ((state.day) * 24) + (state.hour)
        return self.energy_needed[index]

    def getRawData(self, state):
        """
        Returns the raw data (weather conditions) for a given day and hour
        """
        index = ((state.day * 24) + state.hour)
        return self.raw_data[index]

    def getEnergyGained(self, state):
        index = ((state.day) * 24) + (state.hour)
        return self.energy_gained[index]
    
    def initializeState(self, state, weather_reader):
        """
        Given a reader, read in data for first 50 days and use to initialize
        """
        raw_data = []
        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of tuples
            raw_data.append(forecast[0])
            weather_reader.advanceTime()

        # convert weather to power (mega watts)
        for idx in range(len(raw_data)):
            wind_power = self.calculate_wind_power(raw_data[idx].windSpeed)
            solar_power = self.calculate_solar_power(raw_data[idx].sunlight)
            hydro_power = self.calculate_hydro_power()
            if idx == 0:
                state.energy_levels[EnergySource.WIND.value] += wind_power
                state.energy_levels[EnergySource.SOLAR.value] += solar_power
                state.energy_levels[EnergySource.HYDRO.value] += hydro_power
            
            self.capacity[EnergySource.WIND.value] += wind_power
            self.capacity[EnergySource.SOLAR.value] += solar_power
            self.capacity[EnergySource.HYDRO.value] += hydro_power


    def getNumFeatures(self):
        return len(self.features[0])

class ApproximateQLearner():
    """
    Approximate Q Learning Agent
    """

    def __init__(self, alpha, discount):
        self.featExtractor = FeatureExtractor()
        self.weights = [random.random() for _ in range(self.featExtractor.getNumFeatures())]
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
        for idx in range(len(action)):
            result += (featureVector[idx] - action[idx]) * weight[idx]
        for idx in range(len(action), len(featureVector)):
            result += featureVector[idx] * weight[idx]

        renewables = 0
        for a in action:
            renewables += a
        coal_used = self.featExtractor.getEnergyNeeded(state) - renewables
        result -= coal_used
        # print "ACTION, QVAL", action, result
        
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
        for idx in range(len(featureVector)):
            self.weights[idx] = self.weights[idx] + (self.alpha * difference * featureVector[idx])
        
        # normalize weights because everything is a hack
        self.weights = [float(i) / sum(self.weights) for i in self.weights]

class Runner():
    def __init__(self, iterations, max_energy_needed, epsilon, alpha, discount, path_to_data=None, path_to_energy=None, debug=False):
        self.epsilon = epsilon
        self.learner = ApproximateQLearner(alpha, discount)
        self.features = FeatureExtractor(path_to_data, path_to_energy)
        self.state = State(0, 0, self.features)
        self.iterations = iterations
        self.action_space = self.generateLegalActions(max_energy_needed)
        self.debug = debug
    
    def generateLegalActions(self, max_energy_needed):
        """
        Returns an array of actions for the largest energy needed
        """
        incr = max_energy_needed / 100
        increments = range(0,100) + (range(100, 1000, 50) if max_energy_needed > 1000 else range(100, max_energy_needed, 50)) + (range(1000, max_energy_needed, incr) if max_energy_needed > 1000 else list())
        result = [item for item in itertools.product(increments, repeat=3)]
        return result

    def getLegalActions(self, energy_needed):
        actions = []
        for (w, s, h) in self.action_space:
            if (w + s + h) <= energy_needed and self.state.getWind() >= w and self.state.getSolar() >= s and self.state.getHydro() >= h:
                actions.append((w, s, h))
        return actions

    def getAction(self, state, actions, epsilon):
        if random.random() <= epsilon:
            # choose random action
            if self.debug:
                self.debug_file.write("chose random action\n")
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


    def predict_iterate(self):
        # get energy needed for that day/hour
        energy_needed = self.features.getEnergyNeeded(self.state)
        # get legal actions and set in Q-learner
        legalActions = self.getLegalActions(energy_needed)
        self.learner.setLegalActions(legalActions)
        # take optimal action
        action = self.getAction(self.state, legalActions, self.epsilon)
        # calculate next state
        nextState = self.state
        if nextState.hour >= 23:
            nextState.day += 1
            nextState.hour = 0
        else:
            nextState.hour += 1

        energy_gained = list(self.features.getEnergyGained(self.state))
        for idx in range(len(nextState.energy_levels)):
            nextState.energy_levels[idx] = nextState.energy_levels[idx] - list(action)[idx] + self.features.getEnergyGained(self.state)[idx]
            if nextState.energy_levels[idx] > self.features.capacity[idx]:
                energy_gained[idx] = self.features.capacity[idx] - self.state.energy_levels[idx]
                nextState.energy_levels[idx] = self.features.capacity[idx]
        
        current_raw_data = self.features.getRawData(self.state)
        energy_left = list(nextState.energy_levels)
        self.state = nextState
        if self.debug:
            print "DATE: ", current_raw_data.month, current_raw_data.day, current_raw_data.hour
            print "ACTION: " , action
            print "ENERGY_GAINED: ", energy_gained
            print "ENERGY_NEEDED: ", energy_needed
            print "ENERGY_LEFT: ", energy_left
            print "EPSILON: ", self.epsilon
        return current_raw_data, energy_gained, action, energy_left, energy_needed

    def iterate(self):
        # get energy needed and gained for that day/hour
        energy_needed = self.features.getEnergyNeeded(self.state)
        energy_gained = self.features.getEnergyGained(self.state)
        # get legal actions and set in Q-learner
        legalActions = self.getLegalActions(energy_needed)
        self.learner.setLegalActions(legalActions)
        # take optimal action
        action = self.getAction(self.state, legalActions, self.epsilon)
        # calculate next state
        nextState = self.state
        if nextState.hour >= 23:
            nextState.day += 1
            nextState.hour = 0
        else:
            nextState.hour += 1
        
        for idx in range(len(nextState.energy_levels)):
            nextState.energy_levels[idx] = nextState.energy_levels[idx] - list(action)[idx] + energy_gained[idx]
            if nextState.energy_levels[idx] > self.features.capacity[idx]:
                nextState.energy_levels[idx] = self.features.capacity[idx]
        
        # learn from it
        reward = self.calculateReward(self.state, action, self.learner.weights)
        self.learner.update(self.state, action, nextState, reward)
        self.state = nextState
        if self.debug:
            self.debug_file.write("ACTION: " + str(action) + "\n")
            self.debug_file.write("WEIGHTS: " + str(self.learner.weights) + "\n")
            self.debug_file.write("ENERGY_GAINED: " + str(energy_gained) + "\n")
            self.debug_file.write("ENERGY_NEEDED" + str(energy_needed) + "\n")

    def calculateReward(self, state, action, weights):
        """
        Calculates reward for given state based on how much coal used
        """

        renewables = 0
        for power in action:
            renewables = renewables + power
        coal_used = self.features.getEnergyNeeded(state) - renewables

        features = self.features.getFeatures(state)
        #take the min for every feature, not just max of features
        minimum = min(self.features.energy_needed, max(features)) #min bet needed and replenished
        max_feature_index = features.index(max(features))
        diff = minimum - action[max_feature_index]
        reward = (1 / coal_used) + (renewables) + (1/diff)

        if self.debug:
            self.debug_file.write("REWARD" + str(reward) + "\n")

        return reward


    def run(self):
        incr = 0.95
        for idx in range(self.iterations):
            if self.debug:
                self.debug_file.write("-----------------\nITERATION #" + str(idx) + "\n")
            self.iterate()
            if idx % 10 == 0:
                self.epsilon = self.epsilon * incr
                incr = incr * 0.99
            if self.debug:
                self.debug_file.write("ENERGY LEVELS: " + str(self.state.energy_levels) + "\n")
                self.debug_file.write("epsilon: " + str(self.epsilon) + "\n")

if __name__ == '__main__':
    # iterations, max energy, epsilon, alpha, discount
    debug = True
    test = Runner(1000, 70000, 0.5, 0.1, 0.5, debug=debug)
    if debug:
        debug_file = open("debug.txt", 'wb')
        test.debug_file = debug_file
        test.debug_file.write("STARTING WEIGHTS: " + str(test.learner.weights) + "\n")
        test.debug_file.write("STARTING ENERGY LEVELS: " + str(test.state.energy_levels) + "\n")
        test.debug_file.write("CAPACITY: " + str(test.features.capacity) + "\n")
    test.run()


    #pipe final weights to a file
    output_dir = "../src"
    output_filename = 'final_weights.txt'
    output_file = os.path.join(output_dir, output_filename)
    with open(output_file, 'wb') as f:
        pickle.dump(test.learner.weights, f)
        
