import math


class PnL:
    """
    This class tracks a products Pnl via weighted averaging, FIFO and LIFO are not efficient as alternatives as one would
    need to keep track of when every product was bought/sold.
    If the class is used to track some sort of derivative, the PV should be used instead of the market price!
    """

    def __init__(self):
        self._quantity = 0.0
        self._market_price = 0.0
        self.theoretical_ = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

        self._avg_open_price = 0.0
        self._total_quantity = 0.0

    def push(self, price_, quantity_):
        """
        Updates state of pnl instance, price (or PV) and quantity of product
        :param price_: float
        :param quantity_: integer
        :return:
        """
        self._market_price = price_
        self._quantity = quantity_

        self.__update()

    def __update(self):
        """
        wrapper
        :return:
        """

        self._get_pnls()

    def _get_pnls(self, theoretical_=None):
        """
        Here direction of trade is identified
        :param theoretical_: you may optionally define a theoretical exit price instead of the current price or pv
        :return:
        """
        if theoretical_ is None:
            self.theoretical_ = self._market_price
        else:
            self.theoretical_ = theoretical_

        # realize a position

        if self._is_equal():
            self._increase()  # increase position

        else:
            if abs(self._quantity) > abs(self._total_quantity):  # flip position
                self._flip()
            elif abs(self._quantity) == abs(self._total_quantity):  # flatten position
                self._flatten()
            elif abs(self._quantity) < abs(self._total_quantity):  # decrease position
                self._decrease()

    def total_pnl(self):
        """
        Returns total pnl for a product
        :return: float total pnl
        """
        return self.realized_pnl + self.unrealized_pnl

    def _update_open_price(self):
        """
        updates the weighted entering price
        :return:
        """
        self._avg_open_price += (self._quantity / self._total_quantity) * (self._market_price - self._avg_open_price)

    def _update_total_quantity(self):
        """
        Updates the current total quantity of the product
        :return:
        """
        self._total_quantity += self._quantity

    ##########################################

    def _increase(self):
        """
        Updates enter price and unrealized pnl
        :return:
        """
        if (self._total_quantity == 0.0) and (self._quantity == 0.0):
            return

        self._update_total_quantity()
        self._update_open_price()
        self.unrealized_pnl = (self.theoretical_ - self._avg_open_price) * (self._total_quantity)

    def _decrease(self):
        """
        Updates exit price, realized and  unrealized pnl
        :return:
        """
        self._update_total_quantity()
        self.realized_pnl = self.realized_pnl + (self._market_price - self._avg_open_price) * self._quantity * (-1)
        self.unrealized_pnl = (self.theoretical_ - self._avg_open_price) * (self._total_quantity)

    def _flatten(self):
        """
        Updates exit price, realized und resets state of some class variables
        :return:
        """
        self._update_total_quantity()
        self.realized_pnl += (self._market_price - self._avg_open_price) * self._quantity * (-1)

        self._avg_open_price = 0.0
        self._total_quantity = 0.0
        self.unrealized_pnl = 0.0

    def _flip(self):
        """
        Flips position -
        :return:
        """

        self.realized_pnl += (self._market_price - self._avg_open_price) * self._total_quantity  # * (-1)
        self._update_total_quantity()
        self._avg_open_price = self._market_price

        self.unrealized_pnl = (self.theoretical_ - self._avg_open_price) * (self._total_quantity)

    def sign(self, x_):
        """
        Helper to determine sign
        :param x_:
        :return: -1 or 1
        """
        return math.copysign(1, x_)

    def _is_equal(self):
        """
        Checks whether quantities have same sign, special attention needs to be paid to the sign of 0
        :return: bool
        """
        if self._total_quantity == 0:
            self._total_quantity = self._total_quantity * self.sign(self._quantity)

        if self._quantity == 0.0:
            self._quantity = self.sign(self._total_quantity) * self._quantity

        return self.sign(self._quantity) == self.sign(self._total_quantity)