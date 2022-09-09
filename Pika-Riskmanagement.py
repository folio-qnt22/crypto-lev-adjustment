import pandas as pd
import numpy as np
import json
import requests
import time
import datetime
import os

def get_volatility (limit,symbol,interval):
    data = requests.get('https://fapi.binance.com/fapi/v1/klines', params={"symbol" : symbol,
                                                        "interval" : interval, 
                                                        #"startTime" : startTime,
                                                        #"endTime"   : endTime,
                                                        "limit": limit}).json()
    data  = pd.DataFrame(data,columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_vol', 'no_of_trades', 'tb_base_vol', 'tb_quote_vol', 'ignore' ])
    data.iloc[:,1:]=data.iloc[:,1:].astype(float)
    data['time'] = pd.to_datetime(data['timestamp'], unit='ms')
    volatility = ((data['high']-data['low'])/data['open']).mean()*100 #pct_width
    
    return volatility
def get_top20tickers():
    url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df['quoteVolume'] = df['quoteVolume'].astype(float)
    df =df.sort_values(['quoteVolume'], ascending=False)
    #drop columns
    return df['symbol'].values[:20]
def lev_adjustment(HOC_value):
    BTC_volatility = 0.12 # value of (H-L)/O at the period where you perform the best 
    scale_fac  = HOC_value/BTC_volatility
    max_lev    = 15
    normal_lev = 10
    safe_lev   = 7
    
    SL_best = 0.7  # value of the SL at the period where you perform the best 
    SL = SL_best*scale_fac #calculate stop loss
    return np.round(max_lev/scale_fac,2), np.round(normal_lev/scale_fac,2), np.round(safe_lev/scale_fac,2), np.round(SL,2)

Ticker_    = []
Max_lev    = []
Normal_lev = []
Safe_lev   = []
SL_        = []
print('Processing...')
for Ticker in get_top20tickers():
    #Ticker = 'BTCUSDT'
    leverage = lev_adjustment(get_volatility(500,Ticker,'5m'))
    Ticker_   .append(Ticker)
    Max_lev   .append(leverage[0])
    Normal_lev.append(leverage[1])
    Safe_lev  .append(leverage[2])
    SL_       .append(leverage[3])
    
df = pd.DataFrame(Ticker_,columns=['Ticker'])
df['max']    = Max_lev   
df['normal'] = Normal_lev 
df['safe']   = Safe_lev  
df['SL%']         = SL_       
print('------------------------------------')
print('Pika Risk Management Estimation Tool')
print('------------------------------------')
table = df.to_string( index = False, header = True, line_width = 70, justify = 'left')
print(table)
