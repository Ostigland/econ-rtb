
import numpy as np

from boost_functions import boost_optimizer
from boost_mc_sim import Bidder


def boost_simulation(n_bidders):
    n_simulations = 1000000
    n_bins = 500
    learning_rate = 0.0001
    count_simulations = 0
    bidders = ['10', '33', '3', '39', '25', '79', '8', '1']
    bidders = np.random.RandomState(seed=None).permutation(bidders)
    bidders = bidders[-n_bidders:]

    boost_values = {}
    boost_value_lists = {}
    for i in bidders:
        boost_values[i] = 1
        boost_value_lists[i] = []

    bidder_dict = {}
    mean_dict = {}
    sd_dict = {}
    participation_rate_dict = {}
    for i in bidders:
        bidder_dict[i] = Bidder(i, n_bins)
        mean_dict[i] = bidder_dict[i].bid_mean
        sd_dict[i] = np.sqrt(bidder_dict[i].bid_var)
        participation_rate_dict[i] = bidder_dict[i].participation_rate

    print('Boost simulation started for {} bidders.'.format(n_bidders))
    while count_simulations < n_simulations:
        participation_list = []
        bid_dict = {}
        for i in bidders:
            participation, bid = bidder_dict[i].bid_sim()
            participation_list.append(participation)
            if bid > 0:
                bid_dict[i] = bid
        if sum(participation_list) > 1:
            boost_values = boost_optimizer(bid_dict, boost_values, learning_rate)

        for i in boost_values:
            boost_value_lists[i].append(boost_values[i])
        count_simulations += 1

    for i in boost_values:
        boost_values[i] = np.mean(boost_value_lists[i][500000:])

    print('Boost simulation finished with {} bidders'.format(n_bidders))
    result_dict = {'n_bidders':n_bidders, 'boost_values':boost_values,
                   'mean_values':mean_dict, 'var_values':sd_dict,
                   'participation_rate_values':participation_rate_dict}

    return result_dict