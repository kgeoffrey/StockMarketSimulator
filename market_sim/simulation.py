
from .markets import Market
import numpy as np
import pandas as pd
from .traders import *


class Simulation(object):
    
    def __init__(self, length_, num_fund_, num_chart_, fund_dist_, chart_dist_):
        self.length = length_
        
        self.fund_dist = fund_dist_
        self.chart_dist = chart_dist_
        
        self.fundamentalists = self.initialize_fundamentalists(num_fund_)
        self.chartists = self.initialize_chartists(num_chart_)
        
        self.traders = {**self.fundamentalists, **self.chartists}
        
        self.market = Market(self.fund_dist[0])
        self.market_prices = []
        
        self.market_prices_df = None
        self.pnl_df = None
    
    def initialize_fundamentalists(self, num_):
        fundamentalists = {}
        t = 1
        
        for i in range(num_):
            value = abs(int(np.random.normal(*self.fund_dist)))
            trader_id = "fundamentalist_" + str(t)
            fundamentalists[str(trader_id)] = Fundamentalist(value, trader_id)
            t += 1
        return fundamentalists
        
    def initialize_chartists(self, num_):
        chartists = {}
        t = 1
        
        for i in range(num_):
            value = abs(int(np.random.normal(*self.chart_dist)))
            trader_id = "chartist_" + str(t)
            chartists[str(trader_id)] = Chartist(value, trader_id)
            t += 1
        return chartists
    
    def start(self):
        for i in range(self.length):
            price = self.market.market_price
            
            for trader in self.traders.values():
                trader.push(price)
                
                self.check_order(trader)
                
                self.process_matches(self.market.matches) # assign matches
                price = self.market.market_price # update the market price 
                self.market_prices.append(price)
        
        self.create_dfs()
    
    def process_matches(self, matches_):
        if not matches_:
            return
        
        if matches_:
            for match in matches_:
                self.traders[[*match][0]].portfolio.update(*list(match.values())[0])
                #self.traders[[*match][0]].push(*list(match.values())[0]) # something here
                
    def check_order(self, trader_):
        if trader_.order is not None:
            self.market.push(trader_.order)
        else:
            return
    
    def create_dfs(self):
        pnls = {}
        for name in list(self.traders.keys()):
            pnls[name] = self.traders[name].portfolio.pnl.get_total_pnl()
        self.pnl_df = pd.DataFrame(pnls.items(), columns=['Trader', 'PNL'])
        self.market_prices_df = pd.DataFrame(self.market_prices)

