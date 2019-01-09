
import numpy as np
import json
import pandas as pd
import os

from boost_functions import boost_revenue

def sp_bsp_revenue_comparison(experiment):
    """
    DOCUMENTATION
    """
    test_data_path = os.path.join(os.getcwd(), 'auction_dataframes/')
    test_data_file_name = 'test_data'
    test_data_df = pd.read_csv(test_data_path + test_data_file_name)
    test_data_df = test_data_df.reset_index(drop=True)
    boost_data_path = os.path.join(os.getcwd(), 'results/')
    boost_data_file_name = experiment + '.json'
    values = open(boost_data_path + boost_data_file_name, "r")
    result_dict = json.load(values)
    boost_values = result_dict['final_boost_values']

    auction_id = test_data_df['request_id'].drop_duplicates().tolist()
    bsp_revenue = 0
    bsp_winner_dict = {}
    bsp_bid_list = []
    bsp_bid_stats = {'mean':[], 'variance':[]}
    sp_revenue = 0
    sp_winner_dict = {}
    sp_bid_list = []
    sp_bid_stats = {'mean':[], 'variance':[]}

    auction_counter = 0
    data_counter = 0
    while auction_counter < len(auction_id)-1:
        bid_dict = {}
        while test_data_df.iloc[data_counter]['request_id'] == auction_id[auction_counter]:
            if str(test_data_df.iloc[data_counter]['adv_id']) in bid_dict:
                bid_dict[str(test_data_df.iloc[data_counter]['adv_id'])] = \
                    max(bid_dict[str(test_data_df.iloc[data_counter]['adv_id'])],
                        test_data_df.iloc[data_counter]['bid_price'])
            else:
                bid_dict[str(test_data_df.iloc[data_counter]['adv_id'])] = \
                    test_data_df.iloc[data_counter]['bid_price']

            data_counter += 1
        bsp_price, bsp_winner, boost_bid_dict = boost_revenue(bid_dict, boost_values)
        sp_price = sorted(bid_dict.values())[-2]
        sp_winner = sorted(bid_dict, key=bid_dict.__getitem__)[-1]
        bsp_revenue += bsp_price
        sp_revenue += sp_price

        bsp_bid_list.append(bsp_price)
        sp_bid_list.append(sp_price)

        bsp_bid_stats['mean'].append(np.mean(list(boost_bid_dict.values())))
        bsp_bid_stats['variance'].append(np.var(list(boost_bid_dict.values())))
        sp_bid_stats['mean'].append(np.mean(list(bid_dict.values())))
        sp_bid_stats['variance'].append(np.var(list(bid_dict.values())))

        if bsp_winner in bsp_winner_dict:
            bsp_winner_dict[bsp_winner] += 1
        else:
            bsp_winner_dict[bsp_winner] = 1

        if sp_winner in sp_winner_dict:
            sp_winner_dict[sp_winner] += 1
        else:
            sp_winner_dict[sp_winner] = 1

        auction_counter += 1

    result_dict = {'bsp_rev':bsp_revenue, 'sp_rev':sp_revenue,
                   'bsp_winners':bsp_winner_dict, 'sp_winners':sp_winner_dict,
                   'bsp_winning_bids':bsp_bid_list, 'sp_winning_bids':sp_bid_list,
                   'bsp_bid_stats':bsp_bid_stats, 'sp_bid_stats':sp_bid_stats}
    return result_dict

