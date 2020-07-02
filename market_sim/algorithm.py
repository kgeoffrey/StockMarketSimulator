from .portfolio import PortfolioManager


class Algorithms:
    """
    General class for trading strategies
    """
    def __init__(self):
        self.cash = 10000.0 # set via config 
        self.initial_margin = 1.0 # set via config
        self.quantity = 100 # set via config
        self.market_price = 0.0
        self.portfolio = PortfolioManager(self.cash, self.quantity, self.initial_margin, self.trader_id)
        
        self.order = 0

    def set_position(self, position_):
        """
        Accessing portfolio to set a new position
        :param product_: string name of product
        :param position_: float of position
        :return:
        """
        self.portfolio.push(self.market_price, position_)

        self.order = self.portfolio.create_order(self.value)
