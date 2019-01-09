
import numpy as np
import pandas as pd
import os

from boost_functions import boost_revenue

def bsp_revenue_sim(boost_values_list):
    """
    DOCUMENTATION
    """
    test_data_path = os.path.join(os.getcwd(), 'auction_dataframes/')
    test_data_file_name = 'test_data'
    test_data_df = pd.read_csv(test_data_path + test_data_file_name)
    test_data_df = test_data_df.reset_index(drop=True)
    auction_id = test_data_df['request_id'].drop_duplicates().tolist()

    revenue_list = np.zeros(len(boost_values_list)).tolist()
    n_bidders = len(list(boost_values_list[0].values()))

    sp_revenue = 0
    auction_counter = 0
    data_counter = 0
    while auction_counter < 100000:
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

        for i in range(len(revenue_list)):
            revenue, _, _ = boost_revenue(bid_dict, boost_values_list[i])
            revenue_list[i] += revenue
        sp_price = sorted(bid_dict.values())[-2]
        sp_revenue += sp_price
        auction_counter += 1
        if auction_counter % 100000 == 0:
            print('Iterated through {} auctions for {} bidders.'.format(auction_counter, n_bidders))


    result_dict = {'n_bidders':n_bidders, 'revenue_list':revenue_list, 'sp_revenue':sp_revenue}

    return result_dict