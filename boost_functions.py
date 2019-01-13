
import pandas as pd
import os

def boost_optimizer(bid_dict, boost_values, learning_rate):
    """
    DOCUMENTATION
    """
    boost_bid_dict = {}
    for i in bid_dict:
        if i in boost_values:
            boost_bid_dict[i] = bid_dict[i] * boost_values[i]
        else:
            boost_bid_dict[i] = bid_dict[i]
    second_high_bidder, high_bidder = sorted(boost_bid_dict, key=boost_bid_dict.__getitem__)[-2:]

    for i in boost_values and bid_dict:
        if i is not high_bidder:
            max_boost = boost_bid_dict[high_bidder] / bid_dict[i]
            boost_diff = boost_values[i] - max_boost
            new_boost = boost_values[i] - learning_rate * boost_diff
            boost_values[i] = new_boost
        else:
            min_boost = boost_bid_dict[second_high_bidder] / bid_dict[i]
            boost_diff = boost_values[i] - min_boost
            new_boost = boost_values[i] - learning_rate * boost_diff
            boost_values[i] = new_boost

    min_boost = sorted(boost_values.values())[0]
    for i in boost_values:
        boost_values[i] = boost_values[i] / min_boost

    return boost_values

def boost_revenue(bid_dict, boost_values):
    """
    DOCUMENTATION
    """
    boost_bid_dict = {}
    for i in bid_dict:
        if i in boost_values:
            boost_bid_dict[i] = bid_dict[i] * boost_values[i]
        else:
            boost_bid_dict[i] = bid_dict[i]
    second_high_bidder, high_bidder = sorted(boost_bid_dict, key=boost_bid_dict.__getitem__)[-2:]

    if high_bidder in boost_values:
        price = min(boost_bid_dict[second_high_bidder] / boost_values[high_bidder], bid_dict[high_bidder])
    else:
        price = min(boost_bid_dict[second_high_bidder], bid_dict[high_bidder])

    price = max(price, bid_dict[second_high_bidder])

    return price, high_bidder, boost_bid_dict
