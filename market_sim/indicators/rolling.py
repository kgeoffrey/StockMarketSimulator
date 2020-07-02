import math
import numpy as np


class CumulativeStatistics:
    """
    Class tracks cumulative mean, variance, standard deviation
    """
    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def push(self, x_):
        """
        updates state of all variables
        :param x_: value of a time series
        :return:
        """
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x_
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x_ - self.old_m) / self.n  # mean
            self.new_s = self.old_s + (x_ - self.old_m) * (x_ - self.new_m)  # variance

            self.old_m = self.new_m
            self.old_s = self.new_s

    def clear(self):
        self.n = 0

    def mean(self):
        """
        returns mean
        :return: float
        """
        return self.new_m if self.n else 0.0

    def variance(self):
        """
        returns variance
        :return: float
        """
        return self.new_s / (self.n)

    def standard_deviation(self):
        """
        returns standard deviation
        :return: float
        """
        return math.sqrt(self.variance())

    def sharpe_ratio(self):
        return self.mean() / self.standard_deviation()


class Indicators:
    """
    Class for more complicated indicators that may require RollingIndicator instances
    """

    def __init__(self, **kwargs):
        self._arg_list = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, RollingIndicator(value))

        self._diff = 0
        self._diff_old = 0
        self._gain = 0
        self._loss = 0

        self._macd = 0
        self._sosc = 0

    def push(self, *args):
        """
        Update all class variables
        :param args: updates the given indicators
        :return:
        """
        for i, v in enumerate(args):
            getattr(self, self._arg_list[i]).push(v)
        self.update()

    def update(self):
        """
        Updates the giving indicators
        :return:
        """
        ## Update Relative Strength Index

        if self.Close.old_val != 0:
            self._diff = self.Close.new_val - self.Close.series[1]
            self._diff_old = self.Close.series[-1] - self.Close.old_val

            if self._diff >= 0:
                if len(self.Close.series) > self.Close.window:
                    self._gain += self._diff
                    self._gain -= self._diff_old
                else:
                    self._gain += self._diff
            else:
                if len(self.Close.series) > self.Close.window:
                    self._loss += np.abs(self._diff)
                    self._loss -= np.abs(self._diff_old)
                else:
                    self._loss += np.abs(self._diff)

        # Update MACD indicator
        if "macd_long" in self._arg_list:
            if len(self.macd_long.series) > self.macd_long.window:
                self._macd = self.macd_long._ema - self.macd_short._ema

    def relative_strength_index(self):
        """
        Relative Strength Index calculation
        Requires Closing Prices
        :return: float Relative Strength Index
        """

        tmp_loss = self._loss
        if self._loss == 0:
            tmp_loss = np.finfo(float).eps
        rs = self._gain / tmp_loss

        return 100.0 - (100.0 / (1.0 + rs))

    def moving_average_convergence_divergence(self):
        """
        Returns macd
        Requires macd_long and macd_short
        :return: float macd
        """
        return self._macd

    def stochastic_oscillator(self):
        """

        Requires Close, High, Low
        :return: float stochastic oscillator
        """
        min_low = np.min(self.Low.series)
        max_high = np.max(self.High.series)
        self._sosc = 100 * (self.Close.new_val - min_low) / (max_high - min_low)

        return self._sosc


class RollingIndicator:

    def __init__(self, window_):
        self.window = window_
        self.series = []
        self.old_val = 0
        self.new_val = 0
        self._sum = 0
        self._var = 0
        self._var_old = 0
        self._sma = 0
        self._sma_old = 0
        self._ema = 0
        self.c = 2 / float(window_ + 1)

    def _update(self, x_):
        """
        Updates the class variables
        :param x_: value of a time series
        :return:
        """
        self.series.insert(0, x_)
        self.new_val = x_
        self._sum += x_

        if len(self.series) > self.window:
            self.old_val = self.series.pop()
            self._sum -= self.old_val

    def push(self, x_):
        """
        Updates the state of the instance with new value
        :param x_: value of a time series
        :return:
        """
        x = x_ #[self.product].Close
        self._update(x)

        if len(self.series) == self.window:

            # Update Moving Average
            self._sma_old = self._sma
            self._sma = self._sum / float(self.window)

            # Update Exponential Moving Average
            if self._ema == 0:
                self._ema = self._sma
            else:
                self._ema = (self.c * x) + ((1 - self.c) * self._ema)

        # Update moving Variance
        if self.old_val != 0:
            if self._var == 0:
                self._var = np.var([self.series])
            else:
                self._var += (x - self.old_val) * (x - self._sma + self.old_val - self._sma_old) / (self.window)

    # Indicators here:

    def variance(self):
        """
        Variance
        :return: float variance
        """
        if len(self.series) < 2:
            return float('nan')
        else:
            return self._var

    def standard_deviation(self):
        """
        Standard Deviation
        :return: float standard deviation
        """
        if len(self.series) < 2:
            return float('nan')
        else:
            return np.sqrt(self.variance())

    def sma(self):
        """
        returns simple moving average
        :return: float sma
        """
        return self._sma

    def ema(self):
        """
        returns exponential moving average
        :return: float ema
        """
        return self._ema

    def bollinger_band(self, width):
        """
        returns bolling bands
        :param width: the width of the bollinger bands
        :return: tuple of floats (upper and lower limit)
        """
        upperband = self._sma + (self.standard_deviation() * width)
        lowerband = self._sma - (self.standard_deviation() * width)
        return upperband, lowerband

    def rate_of_change(self):
        """
        return the rate of change
        :return: float value of rate of change
        """
        roc = (self.new_val - self.old_val) / self.old_val * 100
        return roc

    def momentum(self):
        """
        return momentum
        :return: float value of momentum
        """
        mom = self.new_val - self.old_val
        return mom
