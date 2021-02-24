# 'The imports below in lines 2-4 are not my work and are public libraries available for Python developers to use'
import math
import random
import time
import xlwt
from xlwt import Workbook
wb = Workbook()

sheet = wb.add_sheet('Sheet')


# 'These are colors hard coded in and pretty self explanatory'
healthy_color = (32, 122, 201)
infected_not_detected_color = (247, 197, 47)
infected_detected_color = (250, 20, 90)
cured_color = (47, 247, 137)
dead_color = (0, 0, 0)
quarantine_zone_color = (201, 180, 167)


class Person: # 'This is the class that has it's own object for each individual ball or person of the Simulation'
    def __init__(self, area_box, radius, state_key, speed_range, mortality_rate, average_recovery_time,
                 average_detection_time, quarantine_on_detection, quarantine_zone, dir_index=None):
        # 'Class variables should be pretty self explanatory, but let me know if you have inquiries'
        self.States = {
                        "Healthy": {"State": "Healthy", "Fill Color": healthy_color, "Quarantined": False},
                        "Infected": {"State": "Infected", "Fill Color": infected_not_detected_color, "Detected": False, "Quarantined": False},
                        "Cured": {"State": "Cured", "Fill Color": cured_color, "Quarantined": False},
                        "Dead": {"State": "Dead", "Fill Color": dead_color, "Quarantined": False}
        }  # 'States dictionary is very useful as it allows to check the state and various conditions of each Person'
        self.area_x1 = area_box[0][0]
        self.area_x2 = area_box[1][0]
        self.area_y1 = area_box[0][1]
        self.area_y2 = area_box[1][1]
        self.radius = radius
        self.state = self.States[state_key]
        self.speed_range = speed_range
        self.speed = int(random.uniform(self.speed_range[0], self.speed_range[1] + 1))
        self.rand_dir_factor = int(random.uniform(50, 150))
        self.mortality_rate = mortality_rate
        self.average_recovery_time = average_recovery_time
        self.average_detection_time = average_detection_time
        self.quarantine_on_detection = quarantine_on_detection
        self.vulnerability_factor = random.uniform(0.0001, 1)
        self.time_until_detection = self.average_detection_time + (self.average_detection_time * (self.vulnerability_factor - 0.5))
        self.time_until_recovery = self.average_recovery_time + (self.average_recovery_time * (self.vulnerability_factor - 0.5))

        if quarantine_zone:  # 'If quarantine zone is enabled, we enable some variables'
            self.q_x_2 = quarantine_zone[0]  # 'The outer limit of quarantine zone'
            self.q_y_2 = quarantine_zone[1]
            self.x = int(random.uniform(self.q_x_2, self.area_x2 + 1))
            self.y = int(random.uniform(self.q_y_2, self.area_y2 + 1))
            self.house_x = self.x
            self.house_y = self.y
            self.quarantine_zone_enabled = True
            try:  # 'Making a individual places in hospital so people in hospital don't all end up on top of each other'
                self.personal_q_zone_place_x = random.randrange(self.area_x1, int(self.q_x_2 - (2*self.radius) + 1))
            except ValueError:
                self.personal_q_zone_place_x = self.q_x_2

            try:
                self.personal_q_zone_place_y = random.randrange(self.area_y1, int(self.q_y_2 - (2*self.radius) + 1))
            except ValueError:
                self.personal_q_zone_place_y = self.q_y_2

        else:
            self.x = int(random.uniform(self.area_x1, self.area_x2 + 1))
            self.y = int(random.uniform(self.area_y1, self.area_y2 + 1))
            self.house_x = self.x
            self.house_y = self.y
            self.quarantine_zone_enabled = False

        fatality_random = random.randrange(100)
        if self.vulnerability_factor * self.mortality_rate * 2 * 100 > fatality_random:
            self.will_die = True
            self.time_until_death = self.time_until_recovery / 2
        else:
            self.will_die = False

        # 'Makes a random direction if one is not given'
        if dir_index is None:
            self.dir_index = random.randrange(5)
        else:
            self.dir_index = dir_index

        self.directions = [[0, 1], [1, 0], [-1, 0], [0, -1], [0, 0]]

    # 'Makes sure Person doesn't exit simulation, called on by the city when moving each person'
    def keep_in_boundaries(self):
        if self.area_x1 > self.x:
            self.dir_index = 1

        elif self.area_x2 < self.x:
            self.dir_index = 2

        elif self.area_y1 > self.y:
            self.dir_index = 0

        elif self.area_y2 < self.y:
            self.dir_index = 3

    def check_if_at_home(self):
        if self.x == self.house_x and self.y == self.house_y:
            return True
        else:
            return False

    def navigate_home(self):
        if self.x < self.house_x - self.radius:
            self.dir_index = 1
            return self.directions[self.dir_index]
        elif self.x > self.house_x + self.radius:
            self.dir_index = 2
            return self.directions[self.dir_index]
        elif self.y < self.house_y - self.radius:
            self.dir_index = 0
            return self.directions[self.dir_index]
        elif self.y > self.house_y + self.radius:
            self.dir_index = 3
            return self.directions[self.dir_index]
        else:
            self.dir_index = 4
            return self.directions[self.dir_index]

    def check_if_in_quarantine_zone(self):
        x_in_zone = False
        y_in_zone = False
        if self.x < self.q_x_2:
            x_in_zone = True

        if self.y < self.q_y_2:
            y_in_zone = True

        if x_in_zone and y_in_zone:
            return True
        else:
            return False

    def determine_directions_to_get_to_quarantine_zone(self):
        if self.q_x_2 < self.x:
            self.dir_index = 2
        elif self.q_y_2 < self.y:
            self.dir_index = 3

        self.speed = self.speed_range[1]

        return self.directions[self.dir_index]

    def move_while_in_quarantine_zone(self):
        if self.personal_q_zone_place_x < self.x:
            self.dir_index = 2
        elif self.personal_q_zone_place_y < self.y:
            self.dir_index = 3
        else:
            self.dir_index = 4

        self.speed = self.speed_range[0] + 1
        return self.directions[self.dir_index]

    def determine_directions_to_get_out_of_quarantine_zone(self):
        x_dist = self.q_x_2 - self.x
        y_dist = self.q_y_2 - self.y

        if x_dist >= 0:
            if y_dist >= 0:
                if x_dist < y_dist:
                    self.dir_index = 1
                else:
                    self.dir_index = 0
            else:
                self.dir_index = 1
        else:
            self.dir_index = 0

        while self.speed == 0:
            self.speed = (random.uniform(self.speed_range[0], self.speed_range[1] + 1))

        return self.directions[self.dir_index]

    def generic_movement_generator(self):
        dir_change = random.randrange(self.rand_dir_factor)
        if dir_change == 1:
            self.dir_index = random.randrange(5)
        direction = self.directions[self.dir_index]

        dir_change = random.randrange(self.rand_dir_factor)
        if dir_change == 1:
            self.speed = int(random.uniform(self.speed_range[0], self.speed_range[1] + 1))

        return direction

    def move(self):
        direction = self.generic_movement_generator()

        # 'Infected, Detected, Quarantine on detection enabled'
        if self.state["State"] == "Infected" and self.state["Detected"] is True and self.quarantine_on_detection:
            # 'If quarantine zone is enabled we are either moving them to quarantine or moving them inside quarantine'
            if self.quarantine_zone_enabled:
                if self.check_if_in_quarantine_zone():
                    direction = self.move_while_in_quarantine_zone()
                else:
                    direction = self.determine_directions_to_get_to_quarantine_zone()
            else:
                self.speed = 0
                return False

        elif self.state["State"] == "Dead":
            self.speed = 0

        elif self.state["State"] != "Infected" and self.quarantine_zone_enabled and self.check_if_in_quarantine_zone():
            direction = self.determine_directions_to_get_out_of_quarantine_zone()

        elif self.state["State"] == "Infected" and self.quarantine_zone_enabled and self.check_if_in_quarantine_zone():
            if not self.state["Detected"]:
                direction = self.determine_directions_to_get_out_of_quarantine_zone()

        elif self.state["Quarantined"] is True:
            direction = self.navigate_home()

        self.x = self.x + (self.speed * direction[0])
        self.y = self.y + (self.speed * direction[1])

    def change_state(self, new_state):
        self.state = self.States[new_state]

    def progress_disease(self, time):
        if self.state["State"] == "Infected":
            if not self.state["Detected"]:
                self.time_until_detection -= time
                if self.time_until_detection <= 0:
                    self.state["Detected"] = True
                    self.state["Fill Color"] = infected_detected_color
                    if self.quarantine_on_detection:
                        self.state["Quarantined"] = True
            elif self.state["Detected"] is True:
                if self.will_die:
                    self.time_until_death -= time
                    if self.time_until_death <= 0:
                        self.change_state("Dead")
                else:
                    self.time_until_recovery -= time
                    if self.time_until_recovery <= 0:
                        self.change_state("Cured")


class City:
    def __init__(self, population_size, initially_infected, spread_factor, speed_range, radius, area_box, city_key,
                 mortality_rate, average_recovery_time, average_detection_time, quarantine_on_detection,
                 quarantine_all_settings, quarantine_zone_percentage, hospital_overflow):
        self.population_size = population_size
        self.initially_infected = initially_infected
        self.spread_factor = spread_factor
        self.speed_range = speed_range
        self.radius = radius
        self.area_box = area_box
        self.area_x1 = area_box[0][0]
        self.area_x2 = area_box[1][0]
        self.area_y1 = area_box[0][1]
        self.area_y2 = area_box[1][1]
        self.connections = {}
        self.city_key = city_key
        self.mortality_rate = mortality_rate
        self.average_recovery_time = average_recovery_time
        self.average_detection_time = average_detection_time
        self.quarantine_on_detection = quarantine_on_detection
        self.quarantine_all_settings = quarantine_all_settings
        self.healthy_count = self.population_size - initially_infected
        self.infected_count = self.initially_infected
        self.infected_detected_count = 0
        self.cured_count = 0
        self.dead_count = 0
        self.hospital_overflow_threshold = hospital_overflow
        self.total_time_ms = 0

        self.q_zone_x2 = self.area_x1 + (quarantine_zone_percentage * (self.area_x2 - self.area_x1))
        self.q_zone_y2 = self.area_y1 + (quarantine_zone_percentage * (self.area_y2 - self.area_y1))

        if quarantine_zone_percentage != 0:
            self.q_zone_pass = [self.q_zone_x2, self.q_zone_y2]

        else:
            self.q_zone_pass = False

        self.all = {}

        i = 1
        for healthy in range(self.population_size - self.initially_infected):
            key = city_key + str(i)
            self.all[key] = Person(area_box, self.radius, "Healthy", self.speed_range, self.mortality_rate,
                                   self.average_recovery_time, self.average_detection_time, self.quarantine_on_detection,
                                   self.q_zone_pass)
            i += 1

        for infected in range(self.initially_infected):
            key = city_key + str(i)
            self.all[key] = Person(self.area_box, self.radius, "Infected", self.speed_range, self.mortality_rate,
                                   self.average_recovery_time, self.average_detection_time, self.quarantine_on_detection,
                                   self.q_zone_pass)
            i += 1

    def update_counts(self):
        self.population_size = 0
        self.healthy_count = 0
        self.infected_count = 0
        self.infected_detected_count = 0
        self.cured_count = 0
        self.dead_count = 0
        for person in self.all.values():
            self.population_size += 1
            if person.state["State"] == "Healthy":
                self.healthy_count += 1
            elif person.state["State"] == "Infected":
                self.infected_count += 1
                if person.state["Detected"]:
                    self.infected_detected_count += 1
            elif person.state["State"] == "Cured":
                self.cured_count += 1
            elif person.state["State"] == "Dead":
                self.dead_count += 1

    def quarantine_all(self):
        if self.quarantine_all_settings:
            # self.update_counts()
            if self.infected_detected_count / self.population_size >= self.quarantine_all_settings[0]:
                for person in self.all.values():
                    person.state["Quarantined"] = True
            elif self.infected_detected_count / self.population_size <= self.quarantine_all_settings[1]:
                for person in self.all.values():
                    if person.state["State"] != "Infected":
                        person.state["Quarantined"] = False
                    else:
                        if person.state["Detected"] is False:
                            person.state["Quarantined"] = False

    def move(self):
        for p in self.all.values():
            p.keep_in_boundaries()
            p.move()

    def output_drawing_parameters(self):
        units = []
        for p in self.all.values():
            units.append((p.state["Fill Color"], (int(p.x), int(p.y)), p.radius))
        if self.q_zone_pass:
            q_zone = (quarantine_zone_color, (int(self.area_x1),
                                              int(self.area_y1),
                                              int(self.q_zone_x2 - self.area_x1),
                                              int(self.q_zone_y2 - self.area_y1)))
            units.insert(0, q_zone)
        return units

    def create_connections(self):
        for infected in self.all.values():
            if infected.state["State"] == "Infected" and infected not in self.connections:
                self.connections[infected] = []
                for healthy in self.all.values():
                    if healthy.state["State"] == "Healthy":
                        old_connections = self.connections[infected]
                        old_connections.append(Connection(infected, healthy, 4, self.radius, self.spread_factor))
                        self.connections[infected] = old_connections

        connection_keys_to_delete = []
        for key in self.connections.keys():
            if key.state["State"] != "Infected":
                connection_keys_to_delete.append(key)

        for key in connection_keys_to_delete:
            self.connections.pop(key)

    def update_connections(self):
        for connection in self.connections.values():
            for c in connection:
                c.update_distance()
                c.update_activity()
                if c.active:
                    c.update_dt()
                    c.check_if_infected()

    def progress_all_disease(self, time):
        for p in self.all.values():
            p.progress_disease(time)

    def update_hospital_overflow(self):
        pass

    def optimized_create_connections(self):
        pass

    def optimized_progress_simulation(self, ms):
        self.total_time_ms += ms
        healthy = 0
        asymptomatic = 0
        symptomatic = 0
        cured = 0
        for i in range(len(self.all.values())):
            p = self.all[self.city_key + str(i)]
            if p.state["State"] == "Healthy":
                self.healthy_count += 1
            elif p.state["State"] == "Infected":
                self.infected_count += 1
                if p.state["Detected"]:
                    self.infected_detected_count += 1
            elif p.state["State"] == "Cured":
                self.cured_count += 1

            p.keep_in_boundaries()
            p.move()

        return


class Connection:
    def __init__(self, infected_person: Person, healthy_person: Person, max_distance_factor, radius, spread_factor):
        self.a = healthy_person
        self.b = infected_person
        self.DT = 0
        self.current_distance = 0
        self.active = True
        self.max_distance = max_distance_factor * radius
        self.radius = radius
        self.spread_factor = spread_factor

    # 'Use every time to update distance, then if distance surpassed max -> Quit this connection'
    def update_distance(self):
        x_dist_squared = (self.a.x - self.b.x) ** 2
        y_dist_squared = (self.a.y - self.b.y) ** 2
        total_distance_squared = x_dist_squared + y_dist_squared
        distance = math.sqrt(total_distance_squared)

        self.current_distance = distance
        return distance

    # 'Only use this method if self.active is True'

    def update_activity(self):
        if self.current_distance > self.max_distance:
            self.active = False
        else:
            self.active = True

        if self.a.state["State"] != "Healthy":
            self.active = False

    def update_dt(self):
        if self.active:
            if self.current_distance < 1:
                self.DT = self.DT + (2*self.radius)
            else:
                self.DT = self.DT + ((2*self.radius)/self.current_distance)

    def check_if_infected(self):
        # 'At 25 cycles per 1 hour, z = 25 would mean direct (close contact) exposure to virus for 1 hour'
        z = self.DT * self.spread_factor
        limit = 50 * self.a.vulnerability_factor
        if z > limit:
            self.a.state = self.a.States["Infected"]
            self.DT = 0


class Simulation:
    def __init__(self, cities, spread_factor, radius, seconds_per_day, mortality_rate, average_recovery_time,
                 average_detection_time, statistic_collection_interval, day_cycle):
        self.cities = cities
        self.spread_factor = spread_factor
        self.radius = radius
        self.mortality_rate = mortality_rate
        self.average_recovery_time = average_recovery_time
        self.average_detection_time = average_detection_time
        self.seconds_per_day = seconds_per_day
        self.total_time_ms = 0
        self.total_time_s = 0
        self.total_sim_hours = 0
        self.curr_sim_hours = 0
        self.sim_days = 0
        self.sci = statistic_collection_interval
        self.day_cycle = day_cycle
        self.daytime_coefficient = 0
        self.live_data_dictionary = {}

        for city in cities:
            self.live_data_dictionary[city] = [[self.total_sim_hours, city.healthy_count, city.infected_count, city.infected_detected_count, city.dead_count]]

    def update_cities(self, new_cities):
        self.cities = new_cities
        self.live_data_dictionary.clear()
        for city in self.cities:
            self.live_data_dictionary[city] = [[self.total_sim_hours, city.healthy_count, city.infected_count, city.infected_detected_count, city.dead_count]]

    def progress_time(self, dt):
        self.total_time_ms += dt
        new_seconds = dt / 1000
        self.total_time_s += new_seconds
        new_hours = 24 * new_seconds / self.seconds_per_day
        self.total_sim_hours += new_hours
        self.curr_sim_hours += new_hours
        if self.curr_sim_hours >= 24:
            self.sim_days += 1
            self.curr_sim_hours = 0

        if self.day_cycle:
            self.daytime_coefficient = math.sin((self.curr_sim_hours - 6) * math.pi / 12) + 1

    def progress_simulations(self, dt):
        hours = 24 * dt / 1000 / self.seconds_per_day
        for city in self.cities:
            city.update_counts()
            city.quarantine_all()
            city.move()
            city.create_connections()
            city.update_connections()
            city.progress_all_disease(hours)

    def collect_data(self, city: City):
        current = self.live_data_dictionary[city]
        current.append([self.total_sim_hours, city.healthy_count, (city.infected_count - city.infected_detected_count), city.infected_detected_count, city.cured_count])
        self.live_data_dictionary[city] = current

    def collect_CDC_style_data(self, city: City):
        pass

    def collect_data_all_cities(self):
        for city in self.cities:
            self.collect_data(city)

    def write_data(self):
        column = 0
        wb._Workbook__worksheets = [wb._Workbook__worksheets[0]]
        sheet.write(0, 0, 'Hours')
        sheet.write(0, 1, 'Healthy')
        sheet.write(0, 2, 'Infected')
        sheet.write(0, 3, 'Symptomatic')
        sheet.write(0, 4, 'Cured')

        my = self.live_data_dictionary[self.cities[0]]
        for i in range(len(my)):
            column += 1
            row = 0
            for z in range(len(my[i])):
                print(my[i][z])
                sheet.write(column, row, my[i][z])
                row += 1

        wb.save('virus data.xls')
