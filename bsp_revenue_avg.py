
import os
import numpy as np
import json
from multiprocessing import Pool

from bsp_boost_sim import boost_simulation
from bsp_revenue_sim import bsp_revenue_sim

if __name__ == '__main__':
    parameter_list = [2, 3, 4, 5, 6]
    parameter_list = sorted(parameter_list*100)

    with Pool(32) as p:
        results = p.map(boost_simulation, parameter_list)

    boost_values = []
    mean_values = []
    sd_values = []
    participation_rate_values = []

    for i in results:
        boost_values += list(i['boost_values'].values())
        mean_values += list(i['mean_values'].values())
        sd_values += list(i['var_values'].values())
        participation_rate_values += list(i['participation_rate_values'].values())

    boost_dict = {'2':[], '3':[], '4':[], '5':[], '6':[]}
    for i in results:
        boost_dict[str(i['n_bidders'])].append(i['boost_values'])

    with Pool(10) as p:
        results = p.map(bsp_revenue_sim, list(boost_dict.values()))

    results.append(boost_values)
    results.append(mean_values)
    results.append(sd_values)
    results.append(participation_rate_values)

    file_path = os.path.join(os.getcwd(), 'results')
    current_result = 'REVENUE_AVG_RESULT_09-01-2019'
    file_name = file_path + '/' + current_result + '.json'
    json.dump(results, open(file_name, "w"))