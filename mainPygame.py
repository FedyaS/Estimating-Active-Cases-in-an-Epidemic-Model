# 'The imports below in lines 2-6 are not my work and are public libraries available for Python developers to use'
import pygame
import PersonClass
import sys
import math
import pygame_gui


# 'Initializing Pygame init and the font so we can output text to window'
pygame.init()
pygame.font.init()

# 'Setting Globals such as the time font variable, dimensions of screen, Pygame display, and clock'
time_font = pygame.font.SysFont('segoeuisemibold', 25)
width = int(pygame.display.Info().current_w / 1.5)
height = int(pygame.display.Info().current_h / 1.5)
screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE)
manager = pygame_gui.UIManager((width, height))
clock = pygame.time.Clock()

# 'Setting up the relation between time in sim and time in real life.
# Also variable such as fps allows us to run the simulation quickly,
# but draw it only at a set fps and save processing power'
cycles_per_day = 600  # 'The simulation is set up depending on this being 600: don't change'
seconds_per_day = 20  # 'Note that 1 day is 600 cycles'
cycles_per_second = cycles_per_day / seconds_per_day
fps = 30  # 'Note that fps must be equal to or less than cps and should be a factor of cps'
cycles_per_frame = cycles_per_second / fps

# 'Setting up global variables related to simulation
# It would be good to be able and change these in GUI. Also good to be able and change some for each city,
# while changing others for all cities:
# Spread factor, speed_range, radius, mortality_rate, a_r_t, a_d_t, _s_c_i should all be universal for all cities
# You should be able to change other variables for each city individually'
population_size = 200
initially_infected = 1
spread_factor = 0.5
speed_range = (0, 5)
radius = 10
mortality_rate = -1
average_recovery_time = 12
average_detection_time = 24
statistic_collection_interval = 24
quarantine_zone_percentage = 0.15
quarantine_on_detection = True
quarantine_all_settings = (1, 0)
hospital_overflow = 0.10


def gen_grid_lines(bb, spacing):
    line_cords = []
    min_x = bb[0][0]
    max_x = bb[1][0]
    min_y = bb[0][1]
    max_y = bb[1][1]

    for x in range(min_x, max_x, spacing):
        line_cords.append([[x, min_y], [x, max_y]])

    for y in range(min_y, max_y, spacing):
        line_cords.append([[min_x, y], [max_x, y]])

    return line_cords


def draw_from_sim(simulation: PersonClass.Simulation):
    for city in simulation.cities:
        units = city.output_drawing_parameters()
        if city.q_zone_pass:
            pygame.draw.rect(screen, units[0][0], units[0][1])
            units.pop(0)

        for u in units:
            pygame.draw.circle(screen, u[0], u[1], u[2])


def draw_lines(line_cords):
    for line in line_cords:
        pygame.draw.aaline(screen, (200, 200, 200), line[0], line[1])


def draw_bare_bones(all_line_cords, temp_line_cords=None):
    screen.fill((255, 255, 255))

    if temp_line_cords:
        draw_lines(temp_line_cords)

    for lines in all_line_cords:
        draw_lines(lines)


def draw_all(c, cpf, simulation: PersonClass.Simulation, line_cords, temp_line_cords):
    if c % cpf == 0:
        screen.fill((255, 255, 255))
        # fc = (simulation.daytime_coefficient * 127)
        # for city in simulation.cities:
        #     pygame.draw.rect(screen, (fc, fc, fc), (city.area_x1, city.area_y1, city.area_x2 - city.area_x1, city.area_y2 - city.area_y1))

        for lines in line_cords:
            draw_lines(lines)

        if temp_line_cords:
            draw_lines(temp_line_cords)

        draw_from_sim(simulation)


def sort_bbox(a, b):
    x1 = a[0]
    x2 = b[0]
    y1 = a[1]
    y2 = b[1]
    mins = [min(x1, x2), min(y1, y2)]
    maxes = [max(x1, x2), max(y1, y2)]

    return [mins, maxes]


def draw_time(simulation: PersonClass.Simulation):
    minutes = math.floor(simulation.total_time_s/60)
    seconds = round(simulation.total_time_s - (60*minutes), 0)

    sim_time_text = f'Simulation Time: {simulation.sim_days} (days) {round(Simulation.curr_sim_hours, 0)} (hours)'
    sim_time_display_surface = time_font.render(sim_time_text, False, (252, 186, 3))
    screen.blit(sim_time_display_surface, (int(width / 2 - (time_font.size(sim_time_text)[0] / 2)), 0))

    real_time_text = f'Real Time: {minutes}:{seconds}'
    real_time_display_surface = time_font.render(real_time_text, False, (252, 186, 3))
    screen.blit(real_time_display_surface, (int(width/2 - (time_font.size(real_time_text)[0] / 2)), int(time_font.get_linesize())))


def draw_counts(healthy, asymptomatic, symptomatic, dead):
    h_text = f"Healthy: {healthy}"
    i_text = f"Infected: {asymptomatic+symptomatic}"
    p_text = f"Presymptomatic: {asymptomatic}"
    a_text = f"Symptomatic: {symptomatic}"
    d_text = f"Recovered: {population_size - healthy - asymptomatic - symptomatic}"

    texts = [h_text, i_text, p_text, a_text, d_text]
    colors = [PersonClass.healthy_color, (235, 128, 14), PersonClass.infected_not_detected_color, PersonClass.infected_detected_color, PersonClass.cured_color]

    start = int(height/2)
    space = int(time_font.get_linesize())
    for i in range(len(texts)):
        dps = time_font.render(texts[i], True, colors[i])
        screen.blit(dps, (0, (start + (space * i))))





cycle = 0

screen.fill((255, 255, 255))
pygame.display.flip()

temp_city_box = []
temp_city_line_cords = []

all_line_cords = []
cities = []

actively_running_sim = False
actively_drawing_sim = False
proceed_past_drawing_cities = False
actively_drawing_grid = False
timer = 0
vaccine_clicker = False

Simulation = PersonClass.Simulation([], spread_factor, radius, seconds_per_day, mortality_rate, average_recovery_time,
                                    average_detection_time, statistic_collection_interval, True)

#hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 100)), text="First button", manager=manager)

# 'This is the main Pygame while loop. It constantly loops through it while the window is active'
healthy, infected, symptomatic, dead = [population_size - initially_infected, initially_infected, 0, 0]
while True:
    dt = clock.tick(cycles_per_second)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not proceed_past_drawing_cities:
            actively_drawing_grid = True
            temp_city_box.clear()
            temp_city_box.append(event.pos)

        if event.type == pygame.MOUSEMOTION and not proceed_past_drawing_cities and actively_drawing_grid:
            temp_city_line_cords = gen_grid_lines(sort_bbox(temp_city_box[0], event.pos), 2 * radius)

        if event.type == pygame.MOUSEBUTTONUP and not proceed_past_drawing_cities:
            actively_drawing_grid = False
            temp_city_box = sort_bbox(temp_city_box[0], event.pos)
            temp_city_line_cords = gen_grid_lines(temp_city_box, 2*radius)

        if event.type == pygame.MOUSEBUTTONDOWN and proceed_past_drawing_cities and vaccine_clicker:
            for city in Simulation.cities:
                for unit in city.all.values():
                    if unit.state["State"] == "Infected":
                        hit_box_radius = 2*unit.radius
                        x1 = unit.x - hit_box_radius
                        x2 = unit.x + hit_box_radius
                        y1 = unit.y - hit_box_radius
                        y2 = unit.y + hit_box_radius

                        if x1 < event.pos[0] < x2 and y1 < event.pos[1] < y2:
                            unit.change_state("Healthy")

        if event.type == pygame.VIDEORESIZE:
            width = event.w
            height = event.h
            screen = pygame.display.set_mode((width, height), flags=pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                vaccine_clicker = True

            if event.key == pygame.K_a:
                if cities:
                    proceed_past_drawing_cities = True

            if event.key == pygame.K_RETURN and not proceed_past_drawing_cities:
                if not temp_city_box:
                    pass

                else:
                    cities.append(PersonClass.City(population_size, initially_infected, spread_factor, speed_range,
                                                   radius, temp_city_box, str(len(cities)), mortality_rate,
                                                   average_recovery_time, average_detection_time,
                                                   quarantine_on_detection, quarantine_all_settings,
                                                   quarantine_zone_percentage, hospital_overflow))
                    Simulation.update_cities(cities)
                    all_line_cords.append(temp_city_line_cords.copy())

                    temp_city_box.clear()
                    temp_city_line_cords.clear()

                    actively_drawing_sim = True

            if event.key == pygame.K_SPACE:
                if proceed_past_drawing_cities:
                    actively_running_sim = True
                    actively_drawing_sim = True

            if event.key == pygame.K_p:
                if proceed_past_drawing_cities:
                    actively_running_sim = False

            if event.key == pygame.K_s:
                if proceed_past_drawing_cities:
                    Simulation.write_data()
                    print(Simulation.live_data_dictionary)

        manager.process_events(event)

    manager.update(dt/1000.0)

    if actively_running_sim:
        Simulation.progress_time(dt)
        Simulation.progress_simulations(dt)
        if cycle % 2 == 0:
            Simulation.collect_data_all_cities()
            cur_data = Simulation.live_data_dictionary[Simulation.cities[0]]
            time, healthy, infected, symptomatic, dead = cur_data[-1][0:]
            print(f"Time: {time}\tHealthy: {healthy}\tInfected: {infected}\tSymptomatic: {symptomatic}\tDead: {dead}")

    if actively_drawing_sim:
        draw_all(cycle, cycles_per_frame, Simulation, all_line_cords, temp_city_line_cords)

    else:
        draw_bare_bones(all_line_cords, temp_city_line_cords)

    draw_time(Simulation)
    draw_counts(healthy, infected, symptomatic, dead)
    manager.draw_ui(screen)
    pygame.display.flip()

    cycle += 1
