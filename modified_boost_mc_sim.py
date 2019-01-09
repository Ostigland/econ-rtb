
import numpy as np
import json
import scipy.interpolate as interpolate
import os

from boost_functions import boost_optimizer, modified_boost_optimizer

class Bidder:
    """
    This class will load the empirical bidder data and then be able to construct each bidder along
    with their ecdf.
    """
    def __init__(self, bidder_id, n_bins, budget_margin):
        """
        DOCUMENTATION
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

        self.win_rate = 0
        self.budget_margin = budget_margin
        self.spending = 0

    def bid_sample(self):
        """
        DOCUMENTATION
        """
        return self.inv_cdf(np.random.rand())

    def bid_sim(self, auction_count):
        """
        DOCUMENTATION
        """
        if np.random.rand() < self.participation_rate:
            participation = True
            bid = self.bid_sample()

            #if self.spending > self.budget(auction_count):
            #    bid = bid * self.budget(auction_count) / self.spending
        else:
            participation = False
            bid = 0

        return participation, bid

    def budget(self, auction_count):
        """
        DOCUMENTATION
        """
        return self.participation_rate * self.bid_mean * self.win_rate * auction_count * (1 + self.budget_margin)


if __name__ == '__main__':
    n_simulations = 500000
    n_bidders = 4
    n_bins = 500
    learning_rate = 0.0001
    budget_margin = 0.3
    count_simulations = 0
    bidders = ['13', '27', '10', '33', '3', '39', '25', '79', '8', '1']
    bidders = bidders[-n_bidders:]

    bidder_dict = {}
    distribution_dict = {}
    for i in bidders:
        bidder_dict[i] = Bidder(i, n_bins, budget_margin)
        distribution_dict[i] = [bidder_dict[i].participation_rate, bidder_dict[i].bid_mean, bidder_dict[i].bid_var]

    boost_values = {}
    boost_value_lists = {}
    for i in bidder_dict:
        boost_values[i] = 1
        boost_value_lists[i] = []

    # for i in range(100000):
    #     participation_list = []
    #     bid_dict = {}
    #     for i in bidder_dict:
    #         participation, bid = bidder_dict[i].bid_sim(count_simulations)
    #         participation_list.append(participation)
    #         if bid > 0:
    #             bid_dict[i] = bid
    #     if sum(participation_list) > 1:
    #         high_bidder = sorted(bid_dict, key=bid_dict.__getitem__)[-1]
    #         bidder_dict[high_bidder].win_rate += 1/100000

    while count_simulations < n_simulations:
        participation_list = []
        bid_dict = {}
        for i in bidder_dict:
            participation, bid = bidder_dict[i].bid_sim(count_simulations)
            participation_list.append(participation)
            if bid > 0:
                bid_dict[i] = bid
        if sum(participation_list) > 1:
            boost_values = boost_optimizer(bid_dict, boost_values, learning_rate)
            boost_bid_dict = {}
            for i in bid_dict:
                if i in boost_values:
                    boost_bid_dict[i] = bid_dict[i] * boost_values[i]
                else:
                    boost_bid_dict[i] = bid_dict[i]
            second_high_bidder, high_bidder = sorted(boost_bid_dict, key=boost_bid_dict.__getitem__)[-2:]
            price = min(boost_bid_dict[second_high_bidder] / boost_values[high_bidder], bid_dict[high_bidder])
            price = max(price, bid_dict[second_high_bidder])
            bidder_dict[high_bidder].spending += price
        else:
            continue

        if count_simulations % 10000 == 0:
            print(boost_values)

        for i in boost_values:
            boost_value_lists[i].append(boost_values[i])

        count_simulations += 1

    result_dict = {'parameters':[n_simulations, n_bidders, n_bins, learning_rate, bidders],
                   'final_boost_values':boost_values,
                   'bidder_distributions':distribution_dict, 'boost_values':boost_value_lists}
    file_path = os.path.join(os.getcwd(), 'results')
    file_name = file_path + '/' + 'MOD_BOOST_SIMULATION_09-01-2019' + '.json'
    json.dump(result_dict, open(file_name, "w"))