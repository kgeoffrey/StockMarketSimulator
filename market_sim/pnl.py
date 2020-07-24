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

        self._realized = 0.0
        self._unrealized = 0.0
        self._enter = 0.0
        self._exit = 0.0
        self._old_enter_amount = 0.0
        self._old_enter_quantity = 0.0
        self._old_exit_amount = 0.0
        self._old_exit_quantity = 0.0
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
        self._update_quantity()

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
        if self._is_not_equal():
            if abs(self._quantity) > abs(self._total_quantity):  # flip position
                self._flip()
            elif abs(self._quantity) == abs(self._total_quantity):  # flatten position
                self._flatten()
            elif abs(self._quantity) < abs(self._total_quantity):  # decrease position
                self._decrease()

        elif self._is_equal():  # increase position
            self._increase()

    def get_total_pnl(self):
        """
        Returns total pnl for a product
        :return: float total pnl
        """
        return self._realized + self._unrealized

    def _update_enter_price(self):
        """
        updates the weighted entering price
        :return:
        """
        self._enter = (self._old_enter_amount + self._quantity * self._market_price) / (
                    self._old_enter_quantity + self._quantity)
        self._old_enter_amount += self._quantity * self._market_price
        self._old_enter_quantity += self._quantity

    def _update_exit_price(self):
        """
        updates the weighted exit price
        :return:
        """
        if self._old_exit_quantity + self._quantity == 0:
            self._exit = 0
        else:
            self._exit = (self._old_exit_amount + self._quantity * self._market_price) / (
                    self._old_exit_quantity + self._quantity)

        self._old_exit_amount += self._quantity * self._market_price
        self._old_exit_quantity += self._quantity

    def _update_quantity(self):
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
        self._update_enter_price()
        self._unrealized = (self.theoretical_ - self._enter) * (self._total_quantity + self._quantity)

    def _decrease(self):
        """
        Updates exit price, realized and  unrealized pnl
        :return:
        """
        self._update_exit_price()
        self._realized = (self._exit - self._enter) * self._old_exit_quantity * (-1)
        self._unrealized = (self.theoretical_ - self._enter) * (self._total_quantity + self._quantity)

    def _flatten(self):
        """
        Updates exit price, realized und resets state of some class variables
        :return:
        """
        self._update_exit_price()
        self._realized = (self._exit - self._enter) * self._old_exit_quantity * (-1)

        self._old_enter_amount = 0.0
        self._old_enter_quantity = 0.0
        self._unrealized = 0.0

    def _flip(self):
        """
        Flips position -
        :return:
        """
        self._flatten()
        self._increase()

    def sign(self, x_):
        """
        Helper to determine sign
        :param x_:
        :return:
        """
        return math.copysign(1, x_)

    def _is_equal(self):
        """
        Checks whether quantities have same sign, special attention needs to be paid to the sign of 0
        :return: bool
        """
        if self._quantity == 0.0:
            self._quantity = self.sign(self._total_quantity) * self._quantity
        return self.sign(self._quantity) == self.sign(self._total_quantity)

    def _is_not_equal(self):
        """
        Checks whether quantities don't have the same sign
        special attention needs to be paid to the sign of 0
        :return: bool
        """
        if self._quantity == 0.0:
            return False
        else:
            return self.sign(self._quantity) != self.sign(self._total_quantity)


class SimplePnL:  # no cash, margin or fees
    """
    This is deprecated method of calculating pnl (NO Weighted average accounting)
    """
    def __init__(self):
        self.total = 0
        self.realized = 0
        self.unrealized = 0
        self.market_price = 0
        self.enter = 0
        self.long = False

    def __push(self, x):
        self.market_price = x
        self.__update()

    def __update(self):
        if self.algorithm.position == 1:
            if not self.long:
                self.enter = self.market_price
                self.long = True
            else:
                self.unrealized = self.market_price - self.enter

        if self.algorithm.position == 0:
            if self.long:
                self.realized = self.market_price - self.enter
                self.total += self.realized
                self.unrealized = 0
                self.enter = 0
                self.long = False
            else:
                pass

    def total_pnl(self):
        return self.total + self.unrealized