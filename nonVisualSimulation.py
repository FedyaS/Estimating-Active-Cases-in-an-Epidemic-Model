import math
import pygame_gui
import pygame
import PersonClass
import sys

cycles_per_day = 600  # 'The simulation is set up depending on this being 600: don't change'
seconds_per_day = 30  # 'Note that 1 day is 600 cycles'
cycles_per_second = cycles_per_day / seconds_per_day
total_cycles = 2251
dt = int((1 / cycles_per_second) * 1000)  # '50'

population_size = 10000
initially_infected = 1
spread_factor = 0.5
speed_range = (0, 5)
radius = 10
mortality_rate = -1
average_recovery_time = 10
average_detection_time = 10
statistic_collection_interval = 24
quarantine_zone_percentage = 0.15
quarantine_on_detection = True
quarantine_all_settings = False
hospital_overflow = 0.10
city_box = [[0, 0], [400, 400]]


cycle = 0

City = PersonClass.City(population_size, initially_infected, spread_factor, speed_range,
                                                   radius, city_box, "0", mortality_rate,
                                                   average_recovery_time, average_detection_time,
                                                   quarantine_on_detection, quarantine_all_settings,
                                                   quarantine_zone_percentage, hospital_overflow)

Simulation = PersonClass.Simulation([City], spread_factor, radius, seconds_per_day, mortality_rate, average_recovery_time,
                                    average_detection_time, statistic_collection_interval, True)

while cycle < total_cycles:
    Simulation.progress_time(dt)
    Simulation.progress_simulations(dt)
    if cycle % 2 == 0:
        Simulation.collect_data_all_cities()
        cur_data = Simulation.live_data_dictionary[Simulation.cities[0]]
        time, healthy, infected, symptomatic, cured = cur_data[-1][0:]
        if infected == 0 and symptomatic == 0:
            cycle = total_cycles
        print(f"Time: {time}\tHealthy: {healthy}\tInfected: {infected}\tSymptomatic: {symptomatic}\tCured: {cured}")

    cycle += 1

Simulation.write_data()
