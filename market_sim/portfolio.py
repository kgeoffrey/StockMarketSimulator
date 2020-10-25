from .pnl import PnL
from .markets import Order


class PortfolioManager:
    """
    This class should take instruction from the ECalgorithm and pass them on to the order handler
    It checks if an order is valid with the given parameters
    ...
    """
    def __init__(self, cash_, stock_, margin_, trader_id_):
        self.cash = cash_
        self.stock = stock_
        self.margin = margin_
        self.trader_id = trader_id_
        self.pnl = self.initialize_pnl()
        self.amount = 0.0
        
        self.outstanding_cash = 0
        self.outstanding_stock = 0
        
        self.market_price = 0.0
        self.position = 0.0
        
    def initialize_pnl(self):
        t = PnL()
        t.push(0.0, self.stock)
        return t

    def push(self, market_price_, position_):
        """
        General entry point for updating state of portfolio
        :param position_: Percentage (float) position between (0 and 1)
        :return: checks if position update
        """
        self.pnl.push(market_price_, 0.0)
        self.market_price = market_price_
        self.position = position_

        if self.position > 0:
            self.buy()
        
        elif self.position < 0:
            self.sell()
        else:
            print("cannot be zero")
            return

    def _get_amount(self):
        """
        Converts a position into an integer order volume
        :return: assigns integer order for _amount invested
        """
        self.amount = int((self.cash * self.position) / (self.market_price * self.margin))

    def update(self, price_, quantity_): # receiving market fills
        self.pnl.push(price_, quantity_)
        
        if quantity_ > 0:
            self.cash -= (quantity_ * price_)
            self.stock += quantity_
            self.outstanding_cash -= (quantity_ * price_)
        if quantity_ < 0:
            self.cash -= (quantity_ * price_)
            self.stock += quantity_
            #self.outstanding_cash += (quantity_ * price_)
            self.outstanding_stock += quantity_

    def buy(self):
        # check if cash is available
        self._get_amount()
        
        if self.cash >= self.outstanding_cash + (self.amount*self.market_price):
            self.outstanding_cash += self.amount*self.market_price
            
        else:
            print("order cannot be processed")
            self.amount = 0

    def sell(self):
        # check if we have enough stock!
        self._get_amount()
        
        if self.stock >= (self.outstanding_stock - self.amount):
            self.outstanding_stock -= self.amount
        else:
            print("order cannot be processed")
            self.amount = 0
    
    def update_market_price(self, market_price_):
        self.pnl.push(market_price_, 0.0)
        
    def create_order(self, value):
        if self.amount != 0:
            if self.trader_id.startswith("fundamentalist"):
                return Order("limit", self.trader_id, self.amount, value)
            elif self.trader_id.startswith("chartist"):
                return Order("market", self.trader_id, self.amount)
            else:
                print("unknown trader type")
        else:
            return

