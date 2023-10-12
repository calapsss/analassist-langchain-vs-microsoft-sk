import pandas as pd
	
dataframe = pd.read_csv("test.csv")

print(dataframe)
military_strength = dataframe['Military Strength']
# military_strength_power_index = dataframe['Military Strength Power Index']
# aircraft_strength = dataframe['Aircraft Strength']
# aircraft_strength_value = dataframe['Aircraft Strength value']
# fighter_interceptor_strength = dataframe['Fighter/Interceptor Strength']
# fighter_interceptor_strength_value = dataframe['Fighter/Interceptor Strength value']
# attack_aircraft_strength = dataframe['Attack Aircraft Strength']
# attack_aircraft_strength_value = dataframe['Attack Aircraft Strength value']
# transport_aircraft_fleet_strength = dataframe['Transport Aircraft Fleet Strength']
# transport_aircraft_fleet_strength_value = dataframe['Transport Aircraft Fleet Strength value']
# trainer_aircraft_fleet = dataframe['Trainer Aircraft Fleet']
# trainer_aircraft_fleet_value = dataframe['Trainer Aircraft Fleet value']
# helicopter_fleet_strength = dataframe['Helicopter Fleet Strength']
print(military_strength)
