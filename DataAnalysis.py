import math
import sys
import random
import pandas as pd
import xlwt
from xlwt import Workbook

collected_data_time_interval = 0.08
analysis_time_interval = 0.8
aggregate_interval = int(analysis_time_interval / collected_data_time_interval)


def calc_new_infections(symptomatic, cured):
    s2 = symptomatic[0]
    c2 = cured[0]
    new_infections = [s2]
    for i in range(1, len(symptomatic)):
        s1 = s2
        s2 = symptomatic[i]
        c1 = c2
        c2 = cured[i]
        live_infections_delta = (s2 - s1) - (c1 - c2)
        new_infections.append(max(0, live_infections_delta))

    return new_infections


def aggregate_values(interval, raw_data):
    aggregate_data = []

    x = 0
    agg_sum = 0

    for i in range(len(raw_data)):
        agg_sum += raw_data[i]
        x += 1

        if x == interval:
            aggregate_data.append(agg_sum)
            agg_sum = 0
            x = 0

    return aggregate_data


def new_infections_estimate(interval, symptomatic, cured):
    all_new = calc_new_infections(symptomatic, cured)
    return aggregate_values(interval, all_new)


def random_sample(healthy, infected, symptomatic, cured, n):
    n1 = n
    positives = 0
    sample_data = [0, 0, 0, 0]
    total = int(healthy + infected + symptomatic + cured)
    hc = 0
    ic = healthy
    sc = healthy + infected
    cc = healthy + infected + symptomatic
    while n > 0 and total > 0:
        x = random.randint(0, total)

        if x <= ic:
            sample_data[0] += 1
            ic -= 1
            sc -= 1
            cc -= 1
        elif x <= sc:
            sample_data[1] += 1
            sc -= 1
            cc -= 1
        elif x <= cc:
            sample_data[2] += 1
            symptomatic -= 1
            cc -= 1
        else:
            sample_data[3] += 1

        total -= 1
        n -= 1

    return (sample_data[1] + sample_data[2]) / (n1 - n)


def random_samples_by_interval(interval, healthy, infected, symptomatic, cured, n):
    estimates = []
    for i in range(0, len(healthy), interval):
        pop = healthy[i] + infected[i] + symptomatic[i] + cured[i]
        infected_guess = random_sample(healthy[i], infected[i], symptomatic[i], cured[i], n) * pop
        estimates.append(infected_guess)

    return estimates


def random_samples_no_cured(interval, healthy, infected, symptomatic, n):
    zeroes = [0 for i in range(len(healthy))]
    return random_samples_by_interval(interval, healthy, infected, symptomatic, zeroes, n)


def random_samples_asymptomatics(interval, healthy, infected, symptomatic, n):
    zeroes = [0 for i in range(len(healthy))]
    asymp_estimates = random_samples_by_interval(interval, healthy, infected, zeroes, zeroes, n)
    for i in range(len(asymp_estimates)):
        shifted_index = i * interval
        asymp_estimates[i] += symptomatic[shifted_index]

    return asymp_estimates


def intervaled_data(interval, infected, symptomatic):
    return [infected[i]+symptomatic[i] for i in range(0, len(infected), interval)]


def data_analysis(healthy, infected, symptomatic, cured, n):
    interval = aggregate_interval
    actual_live_infections = intervaled_data(interval, infected, symptomatic)
    print("actual_live_infections")
    cdc_new_cases = new_infections_estimate(interval, symptomatic, cured)
    print("cdc_new_cases")
    pure_rs = random_samples_by_interval(interval, healthy, infected, symptomatic, cured, n)
    print("pure_rs")
    cured_exclusion_rs = random_samples_no_cured(interval, healthy, infected, symptomatic, n)
    print("cured_exclusion_rs")
    asymptomatic_rs = random_samples_asymptomatics(interval, healthy, infected, symptomatic, n)
    print("asymptomatic_rs")

    wb = Workbook()
    sheet = wb.add_sheet('Analysis')

    list = [actual_live_infections, cdc_new_cases, pure_rs, cured_exclusion_rs, asymptomatic_rs]

    column = -1
    wb._Workbook__worksheets = [wb._Workbook__worksheets[0]]

    sheet.write(0, 0, 'Actual Live Infections')
    sheet.write(0, 1, 'CDC New Cases')
    sheet.write(0, 2, 'Pure RS')
    sheet.write(0, 3, 'Cured Exclusion RS')
    sheet.write(0, 4, 'Asymptomatic RS')

    for i in range(len(list)):
        column += 1
        row = 1
        for z in range(len(list[i])):
            print(list[i][z])
            sheet.write(row, column, float(list[i][z]))
            row += 1

    wb.save('throwaway.xls')

    return [actual_live_infections, cdc_new_cases, pure_rs, cured_exclusion_rs, asymptomatic_rs]


df = pd.read_excel('virus_data-10k 3x3.xls')

row_num = 1127
healthy = []
infected = []
symptomatic = []
cured = []

for i in range(row_num):
    healthy.append(df.iloc[i, 1])
    infected.append(df.iloc[i, 2])
    symptomatic.append(df.iloc[i, 3])
    cured.append(df.iloc[i, 4])

print(data_analysis(healthy, infected, symptomatic, cured, 100))




