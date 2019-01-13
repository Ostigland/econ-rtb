
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

def boost_tuning(parameter_list):
    """
    DOCUMENTATION
    """
    adv_n, learning_rate = parameter_list
    data_path = os.path.join(os.getcwd(), 'auction_dataframes')
    file_name = 'sorted_aggregated_data'
    data_df = pd.read_csv(data_path + '/' + file_name).iloc[20001:]
    advertiser = ['46', '27', '10', '33', '3', '39', '25', '79', '1', '8']
    advertiser = advertiser[-adv_n:]
    auction_id = data_df['request_id'].drop_duplicates().tolist()
    data_df = data_df.reset_index(drop=True)
    boost_values = {}
    for i in advertiser:
        boost_values[i] = 1

    auction_counter = 0
    data_counter = 0
    while auction_counter < 100000:
        bid_dict = {}
        while data_df.iloc[data_counter]['request_id'] == auction_id[auction_counter]:
            if str(data_df.iloc[data_counter]['adv_id']) in bid_dict:
                bid_dict[str(data_df.iloc[data_counter]['adv_id'])] = \
                    max(bid_dict[str(data_df.iloc[data_counter]['adv_id'])], data_df.iloc[data_counter]['bid_price'])
            else:
                bid_dict[str(data_df.iloc[data_counter]['adv_id'])] = data_df.iloc[data_counter]['bid_price']

            data_counter += 1
        boost_values = boost_optimizer(bid_dict, boost_values, learning_rate)
        auction_counter += 1
        if auction_counter % 10000 == 0:
            print('Iterated through {} auctions'.format(auction_counter))

    result_dict = {'parameters':parameter_list, 'boost_values':boost_values}
    return result_dict

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