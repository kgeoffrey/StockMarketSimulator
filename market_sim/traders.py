from .algorithm import Algorithms
from .indicators import rolling


class Fundamentalist(Algorithms):
    
    def __init__(self, value_, trader_id_):
        self.value = value_
        self.trader_id = trader_id_
        Algorithms.__init__(self)
    
    def push(self, market_price_):
        self.market_price = market_price_
        self.portfolio.update_market_price(self.market_price)
        self.signal()
    
    def signal(self):
        
        if self.market_price < self.value:
            print("buy")
            self.set_position(0.3)
            
        if self.market_price >= self.value:
            print("sell")
            self.set_position(-0.3)


class Chartist(Algorithms):
    
    def __init__(self, window_, trader_id_):
        self.value = window_
        self.trader_id = trader_id_
        Algorithms.__init__(self)
        
        self.momentum = rolling.RollingIndicator(window_)
    
    def push(self, market_price_):
        self.market_price = market_price_
        self.portfolio.update_market_price(self.market_price)
        self.signal()
    
    def signal(self):
        self.momentum.push(self.market_price)
        if self.momentum.momentum() > 0:
            print("buy")
            self.set_position(0.3)
            
        if self.momentum.momentum() <= 0:
            print("sell")
            self.set_position(-0.3)
    
            

    