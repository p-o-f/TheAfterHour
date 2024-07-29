import pandas as pd
import robin_stocks.robinhood as r
from robin_stocks.robinhood.helper import *
from robin_stocks.robinhood.urls import *
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from dotenv import load_dotenv
import os
load_dotenv()

u = os.environ.get('rh_username')
p = os.environ.get('rh_password')

def start(email, pw):
    try:
        login = r.login(email, pw)
        print("Logged in!")
    except:
        print("Error while trying to login.")



def get_watchlist_by_id(url_suffix = "e8ef4c1f-244f-4db5-a582-c4c37f3c8e8e", info="results"): # Default is 100 most popular: https://robinhood.com/lists/robinhood/e8ef4c1f-244f-4db5-a582-c4c37f3c8e8e
    """Returns a list of information related to the stocks in a single watchlist.

    :param url_suffix: The url suffix of the watchlist to get data from.
    :type name: Optional[str]
    :param info: Will filter the results to get a specific value.
    :type info: Optional[str], put "results" or None
    :returns: Returns a list of dictionaries that contain the instrument urls and a url that references itself.

    keys for each element in the returned list:
    dict_keys(['created_at', 'id', 'list_id', 'object_id', 'object_type', 'owner_type', 'updated_at', 
    'weight', 'open_price', 'open_price_direction', 'market_cap', 'name', 'open_positions', 'symbol', 
    'uk_tradability', 'us_tradability', 'state', 'ipo_access_status', 'holdings', 'one_day_dollar_change', 
    'one_day_percent_change', 'one_day_rolling_dollar_change', 'one_day_rolling_percent_change', 'price', 'total_return_percentage'])

    most relevant keys: market_cap, name, symbol, us_tradability, one_day_rolling_dollar_change, one_day_rolling_percent_change, price

    examples:
    print(get_watchlist_by_id()[0]) 
    print(get_watchlist_by_id()[0]["market_cap"])

    TODO do function annotation stuff like this one ^^ above later to cleanup
    """
    premade_lists_url_base = "https://api.robinhood.com/midlands/lists/items/"
    data = request_get(premade_lists_url_base, 'list_id', {'list_id':url_suffix})
    return(filter_data(data, info))



def get_general_category(industry):
    #print(set(df["industry"]))
    #print(df[df['symbol'] == 'PYPL']) <-- print all rows where symbol is PYPL

    ## TODO If needed, use the below commented code later to add more to the classification_map
    # Check if the 'Category' column matches 'Unknown'
     #matching_rows = df[df['category'] == 'Unknown']

    # Print the matching rows
     #print(matching_rows)

    classification_map = {
        'Semiconductors': 'Technology',
        'Internet Software/Services': 'Technology',
        'Internet Retail': 'Technology',
        'Computer Processing Hardware': 'Technology',
        'Electronic Production Equipment': 'Technology',
        'Telecommunications Equipment': 'Technology',
        'Electronics/Appliance Stores': 'Technology',
        'Electronic Equipment/Instruments': 'Technology',
        'Packaged Software': 'Technology',
        'Information Technology Services': 'Technology',
        'Investment Trusts Or Mutual Funds': 'Misc (probably an ETF)',
        'Property/Casualty Insurance': 'Finance and Investments',
        'Finance/Rental/Leasing': 'Finance and Investments',
        'Investment Managers': 'Finance and Investments',
        'Investment Banks/Brokers': 'Finance and Investments',
        'Major Banks': 'Finance and Investments',
        'Pharmaceuticals: Major': 'Healthcare and Pharmaceuticals',
        'Pharmaceuticals: Other': 'Healthcare and Pharmaceuticals',
        'Biotechnology': 'Healthcare and Pharmaceuticals',
        'Integrated Oil': 'Energy',
        'Oil & Gas Pipelines': 'Energy',
        'Beverages: Non-Alcoholic': 'Consumer Goods and Services',
        'Restaurants': 'Consumer Goods and Services',
        'Apparel/Footwear': 'Consumer Goods and Services',
        'Specialty Stores': 'Consumer Goods and Services',
        'Other Consumer Services': 'Consumer Goods and Services',
        'Airlines': 'Transportation and Aerospace',
        'Other Transportation': 'Transportation and Aerospace',
        'Aerospace & Defense': 'Transportation and Aerospace',
        'Motor Vehicles': 'Transportation and Aerospace',
        'Broadcasting': 'Media and Entertainment',
        'Movies/Entertainment': 'Media and Entertainment',
        'Advertising/Marketing Services': 'Media and Entertainment',
        'Industrial Machinery': 'Industrial and Manufacturing',
        'Miscellaneous Commercial Services': 'Industrial and Manufacturing',
        'Agricultural Commodities/Milling': 'Industrial and Manufacturing',
        'Real Estate Investment Trusts': 'Real Estate and Hospitality',
        'Hotels/Resorts/Cruise lines': 'Real Estate and Hospitality',
        'Wireless Telecommunications': 'Technology'  # Example of adding additional classifications
    }

    if classification_map.get(industry) != None:
         return classification_map[industry] 
    return 'Misc (probably an ETF)' #TODO decide if I want to keep this at some point; temporary probably?



def create_watchlist_df(url_suffix = "e8ef4c1f-244f-4db5-a582-c4c37f3c8e8e", info="results"): # Default is 100 most popular: https://robinhood.com/lists/robinhood/e8ef4c1f-244f-4db5-a582-c4c37f3c8e8e
    #TODO this is most likely terrible performance wise; hopefully optimize it at some point
    
    raw_list = get_watchlist_by_id() #TODO FIX THIS!!!! <---------------------------------------- ! ! ! !  get_watchlist_by_id(url_suffix)
    
    data = { #TODO fix this bc api calls are fked
        "market_cap": [r["market_cap"] for r in raw_list],
        "name": [r["name"] for r in raw_list],
        "symbol": [r["symbol"] for r in raw_list],
        "us_tradability": [r["us_tradability"] for r in raw_list],
        "one_day_rolling_dollar_change": [r["one_day_rolling_dollar_change"] for r in raw_list],
        "one_day_rolling_percent_change": [r["one_day_rolling_percent_change"] for r in raw_list],
        "current_price": [r["price"] for r in raw_list],
        "last_extended_hours_price": r.get_quotes([r["symbol"] for r in raw_list], "last_extended_hours_trade_price"), # equivalent to calling r.get_quotes("TSLA", "last_extended_hours_trade_price")
        "adjusted_previous_close_price": r.get_quotes([r["symbol"] for r in raw_list], "adjusted_previous_close"), #notably, r.get_latest_price("TSLA", True) gives same as the above ^
        "is_halted": r.get_quotes([r["symbol"] for r in raw_list], "trading_halted"),
        "industry": r.get_fundamentals([r["symbol"] for r in raw_list], "industry"),
        "category": map(get_general_category, r.get_fundamentals([r["symbol"] for r in raw_list], "industry"))
    }

    df = pd.DataFrame(data)

    # Replace empty strings and NaN values in the 'industry' column with 'Misc (probably an ETF)'
    df['industry'] = df['industry'].replace('', 'Misc (probably an ETF)').fillna('Misc (probably an ETF)') #temporary?

    return df



##### Simple prototype that works fine for basic functionality; TODO iterate on it in terms of UI/UX mainly and use it as a base/reference
'''
def create_heat_map(dataframe):
    header = "Overnight Trading Stock Market Heat Map"
    
    palette = {-3: "#e74b3e", -2: "#b44b48", -1: "#84494e", 0: "#414553", 1: "#457351", 2: "#509957", 3: "#63c667"}
    black = "#262930"

    # Exclude GOOGL from the dataframe
    dataframe = dataframe[dataframe['symbol'] != 'GOOGL']

    # Create a new column that combines the name with the percentage change and create symbol_with_change column with HTML formatting
    dataframe.loc[:, 'symbol_with_change'] = dataframe.apply(
        lambda row: f"<span style='font-size: larger'>{row['symbol']}</span><br>{row['one_day_rolling_percent_change']:+.2f}%", axis=1
    )

    # Create Plotly treemap
    fig = px.treemap(
        dataframe,
        path=[px.Constant(header), 'category', 'industry', 'symbol_with_change'],
        values='market_cap',
        color='one_day_rolling_percent_change'
    )

    return fig
'''



def create_heat_map(dataframe):    
    palette = {
        -3: "#e74b3e", -2: "#b44b48", -1: "#84494e",
        0: "#414553", 1: "#457351", 2: "#509957", 3: "#63c667"
    }
    black = "#262930"
    
    # Define a custom diverging color scale with more granularity around ±1%
    color_scale = [
        [0.0, palette[-3]], [0.125, palette[-2]], [0.25, palette[-1]], 
        [0.5, palette[0]], [0.75, palette[1]], [0.875, palette[2]], [1.0, palette[3]]
    ]

    # Exclude GOOGL from the dataframe
    dataframe = dataframe[dataframe['symbol'] != 'GOOGL']

    # Apply a power transformation to the market cap values
    power = 0.6  # Adjust this value to control the transformation strength
    dataframe['transformed_market_cap'] = np.power(dataframe['market_cap'], power)

    # Create a new column that combines the name with the percentage change and create symbol_with_change column with HTML formatting
    dataframe['symbol_with_change'] = dataframe.apply(
        lambda row: f"<span style='font-size: larger; color: white;'>{row['symbol']}</span><br><span style='color: white;'>{row['one_day_rolling_percent_change']:+.2f}%</span>",
        axis=1
    )

    # Create Plotly treemap
    fig = px.treemap(
        dataframe,
        path=['category', 'symbol_with_change'], # ['category', 'industry', 'symbol_with_change'], ruins the scaling, for now leave the 'industry' out
        values='transformed_market_cap',
        color='one_day_rolling_percent_change',
        color_continuous_scale=color_scale, 
        range_color=(-3,3),
        custom_data=['one_day_rolling_percent_change', "current_price", "name"]  
    )

    # Adjust annotation position and style
    fig.update_traces(
        textposition='middle center',
        hovertemplate='<b>%{label}</b><br>' +
                    '%{customdata[2]}<br>'+
                    #'Rolling % change: %{customdata[0]:.2f}%<br>' +
                    'Last price: $%{customdata[1]:,.2f}<br>' + 
                    '<extra></extra>'
    )

    # Modify the colorbar
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Rolling % Change",
            thicknessmode="pixels", thickness=20,
            lenmode="fraction", len=0.33,
            yanchor="bottom", y=-0.1,
            xanchor="center", x=0.5,
            orientation="h",
            )
            #https://community.plotly.com/t/how-to-change-the-background-color-of-the-html-page/67356 TODO
    )



    return fig




def main():
     start(u, p)

     df = create_watchlist_df() #can pass in a link URL here optionally
     #print(df)

     #print(set(df["industry"]))
     print(df[df['symbol'] == 'PYPL']) #TODO fix the categories using this, for example Visa and PYPL are under industrial and manufacturing?? maybe api is returning wrong..

     fig = create_heat_map(df)
     fig.show()

if __name__ == "__main__":
    main()



#TODO for later, -----> print(r.get_quotes("TSLA")) get bid ask etc if needed
#TODO important for deployment: https://community.render.com/t/what-is-the-correct-start-command-for-a-python-dash-app/5740/2

# BTW, if this gets ran [the program as a whole], this will happen:
# Error:
# SettingWithCopyWarning: A value is trying to be set on a copy of a
# slice from a DataFrame

# As explained in the Source, this warning is usually safe to ignore. You
# can disable it by running the following:
  # import pandas as pd
  # pd.options.mode.chained_assignment = None  # default='warn'