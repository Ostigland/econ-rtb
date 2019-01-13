
import numpy as np
import scipy.interpolate as interpolate
import os
import json

from boost_functions import boost_optimizer

class Bidder:
    """
    This class will load the empirical bidder data and then be able to construct each bidder along
    with their ecdf.
    """
    def __init__(self, bidder_id, n_bins):
        """

        :param bidder_id:
        """
        file_path = os.path.join(os.getcwd(), 'bidder_data')
        file_name = file_path + '/sorted_' + bidder_id + '.json'
        data = open(file_name, "r")
        bidder_dict = json.load(data)

        self.participation_rate = bidder_dict['participation_rate']
        self.bids = bidder_dict['bids']
        self.bid_mean = np.mean(self.bids)
        self.bid_var = np.var(self.bids)
        self.hist, self.bin_edges = np.histogram(self.bids, n_bins, range=[0, 5], density=True)
        cum_values = np.zeros(self.bin_edges.shape)
        cum_values[1:] = np.cumsum(self.hist * np.diff(self.bin_edges))
        self.inv_cdf = interpolate.interp1d(cum_values, self.bin_edges)

    def bid_sample(self, n_sample):
        """

        :param n_sample:
        :return:
        """
        return self.inv_cdf(np.random.rand())

    def bid_sim(self):
        """

        :return:
        """
        if np.random.rand() < self.participation_rate:
            participation = True
            bid = self.bid_sample(1)
        else:
            participation = False
            bid = 0

        return participation, bid

if __name__ == '__main__':
    n_simulations = 500000
    n_bidders = 3
    n_bins = 500
    learning_rate = 0.0001
    count_simulations = 0
    bidders = ['13', '27', '10', '33', '3', '39', '25', '79', '8', '1']
    bidders = bidders[-n_bidders:]

    boost_values = {}
    boost_value_lists = {}
    for i in bidders:
        boost_values[i] = 1
        boost_value_lists[i] = []

    bidder_dict = {}
    distribution_dict = {}
    for i in bidders:
        bidder_dict[i] = Bidder(i, n_bins)
        distribution_dict[i] = [bidder_dict[i].participation_rate, bidder_dict[i].bid_mean, bidder_dict[i].bid_var]

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
        else:
            continue

        if count_simulations % 10000 == 0:
            print(boost_values)

        for i in boost_values:
            boost_value_lists[i].append(boost_values[i])

        count_simulations += 1

    for i in boost_values:
        boost_values[i] = np.mean(boost_value_lists[i][400000:])

    result_dict = {'parameters':[n_simulations, n_bidders, n_bins, learning_rate, bidders],
                   'final_boost_values':boost_values,
                   'bidder_distributions':distribution_dict, 'boost_values':boost_value_lists}
    file_path = os.path.join(os.getcwd(), 'results')
    file_name = file_path + '/' + 'BOOST_SIMULATION_12-01-2019_3' + '.json'
    json.dump(result_dict, open(file_name, "w"))
