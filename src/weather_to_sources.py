from data_reader import WeatherData
from data_reader import RandomReader
from enums import EnergySource

class State():
    """
    State for the Q-learning situation
    """
    def __init__(self, day, hour):
        self.energy_levels = [] #energy left, indexed by EnergySource enum
        self.day = day
        self.hour = hour

    def updateEnergy(self, energy_used):
        """
        Pass in array of amounts of energy consumed, indexed by EnergySource
        """
        for index in range(len(energy_levels)):
            energy_levels[index] = energy_levels[index] - energy_used[index]

class FeatureExtractor():
    def __init__(self):
        self.raw_data = []
        self.features = []
        self.energy_needed = [] #read in from excel sheet/json -- this is the energy needed [MW] per hour
        self.readData()

    def readData(self):
        """
        Reads in weather data from a file and stores it (in self.raw_data)
        """

        #read in weather data from csv/call scraper

        #read in all days at once?
        weather_reader = RandomReader(365) #365 days, with 24 tuples of (wind,sun) in each day?
        while weather_reader.canGetForecast():
            forecast = weather_reader.getForecast() #forecast = list of tuples
            for weather_tuple in forecast:
                #convert wind from miles/hour to meters/second
                weather_tuple.windSpeed = weather_tuple.windSpeed/2.237
            self.raw_data.append(forecast)
            weather_reader.advanceTime()


        #convert weather to power (watts)
        #go through self.data and calculate power for the hour
        for day in self.raw_data:
            for weather_tuple in day:
                wind_power = self.calculate_wind_power(weather_tuple.windSpeed)
                solar_power = self.calculate_solar_power(weather_tuple.sunlight)
                hydro_power = self.calculate_hydro_power()
                self.features.append((wind_power, solar_power, hydro_power))

        #fill in self.energy_needed!!!!
        #convert MW to watts


    def calculate_wind_power(self, wind_speed):
        #returns wind power in watts

        air_density = 1 #could change but isn't that important
        area = 7853 #(max in texas onshore is 130 feet diameter, radius = 50ft, pi*r^2 == 7853)
        return .5*air_density*area*(wind_speed ** 3)


    def calculate_solar_power(self, sun_hours):
        #returns solar power in watts

        fudge_factor = .75
        panel_wattage = 144000000 #http://www.ercot.com/gridinfo/resource (144 megawatts capactity in Travis county)
        return panel_wattage*sun_hours*fudge_factor

    def calculate_hydro_power(self):
        #returns hydro power in watts

        efficiency = .8 #average hydroelectric plant efficiency
        water_density = 997
        flow_rate = 1 #may vary because of rain but usually doesn't
        gravity_acceleration = 9.8
        height_diff = 100.5 #austin's tom miller dam

        return efficiency*water_density*flow_rate*gravity_acceleration*height_diff

    def getFeatures(self, state):
        """
        Returns the features for a given day and hour
        """
        index = ((state.day - 1) * 24) + (state.hour - 1)
        return self.features[index]

    def getEnergyNeeded(self, state):
        index = ((state.day - 1) * 24) + (state.hour - 1)
        return self.energy_needed[index]

class ApproximateQLearner():
    """
    self.weights: list storing the weights, index matches up with features
    action representation: int matching up with EnergySource enum
    """

    def __init__(self):
        self.weights = [0 for _ in range(len(WeatherConditions))]
        self.featExtractor = FeatureExtractor()
        self.discount = 0.5


    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
        Should return Q(state,action) = w * featureVector
        where * is the dotProduct operator
        """
        featureVector = self.featExtractor.getFeatures()
        weight = self.getWeights()
        result = weight * featureVector
        return result

    def computeValueFromQValues(self, state):
    """
        Returns Q value that comes from taking optimal action in this state
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
        featureVector = self.featExtractor.getFeatures(state, action)
        difference = reward + (self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state,action)
        for feature in featureVector:
            self.weights[feature] = self.getWeights()[feature] + (self.alpha * difference * featureVector[feature])

class Runner():
    def __init__(self):
        learner = ApproximateQLearner()
        features = FeatureExtractor()
    
    def calculateReward(self, state, action):
        """
        Calculates reward for given state based on how much coal used
        """
        #energy needed that hour - how much coal we used that hour ==> 
        renewables = 0
        for power in features.getFeatures(state):
            renewables = renewables + power

        coal_used = features.getEnergyNeeded(state) - renewables

        return -coal_used

if __name__ == '__main__':
    test = FeatureExtractor()

