import pandas as pd


class Technical:
    """
    df must contain Close, Open, High, Low, Volume for a given time series
    """

    def __init__(self, df):
        self.df = df

    def moving_average(self, n):
        """Calculate the Simple moving average for the given period.
        :param n: time period
        :return: pandas.DataFrame
        """
        MA = pd.Series(self.df['Close'].rolling(n, min_periods=n).mean(), name='MA_' + str(n))
        self.df = self.df.join(MA)

        return self.df

    def exponential_moving_average(self, n):
        """ Calculates the Exponential Moving Average for given time period.
        :param n: time period
        :return: pandas.DataFrame
        """
        EMA = pd.Series(self.df['Close'].ewm(span=n, min_periods=n).mean(), name='EMA_' + str(n))
        self.df = self.df.join(EMA)

        return self.df

    def momentum(self, n):
        """ Calculates the Momentum Indicator for given time period.
        :param n: time period
        :return: pandas.DataFrame
        """
        M = pd.Series(self.df['Close'].diff(n), name='Momentum_' + str(n))
        self.df = self.df.join(M)

        return df

    def rate_of_change(self, n):
        """Calculates the rate of change for given time period
        :param n: time period
        :return: pandas.DataFrame
        """
        M = self.df['Close'].diff(n - 1)
        N = self.df['Close'].shift(n - 1)
        ROC = pd.Series(M / N, name='ROC_' + str(n))
        self.df = self.df.join(ROC)

        return self.df

    def bollinger_bands(self, n, num_of_std):
        """Calculates Bollinger Bands for given time period with given scaling factor.
        :param n: time period
        :param num_of_std: Scaling factor for standard deviation
        :return: pandas.DataFrame
        """
        rolling_mean = pd.Series(self.df['Close'].rolling(n, min_periods=n).mean())
        rolling_std = pd.Series(self.df['Close'].rolling(n, min_periods=n).std())

        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)

        up = pd.Series(upper_band, name='upper_bband' + str(n))
        down = pd.Series(lower_band, name='lower_bband' + str(n))
        self.df = self.df.join(up, down)

        return self.df

    def stochastic_oscillator_d(self, n):
        """Calculate stochastic oscillator %D for given data.
        :param n: time period
        :return: pandas.DataFrame
        """
        SOk = pd.Series((self.df['Close'] - self.df['Low']) / (self.df['High'] - self.df['Low']), name='SO%k')
        SOd = pd.Series(SOk.ewm(span=n, min_periods=n).mean(), name='SO%d_' + str(n))

        self.df = self.df.join(SOd)

        return self.df

    def standard_deviation(self, n):
        """Calculate Standard Deviation for given time period of closing price.
        :param n: time period
        :return: pandas.DataFrame
        """
        self.df = self.df.join(pd.Series(self.df['Close'].rolling(n, min_periods=n).std(), name='STD_' + str(n)))

        return self.df

    def relative_strength_index(self, n):
        """Calculate relative strength index for given time period
        :param n: time period
        :return: pandas.DataFrame
        """
        delta = self.df['Close'].diff()
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0
        Rolling_Up = dUp.rolling(n, min_periods=n).mean()
        Rolling_Down = dDown.rolling(n, min_periods=n).mean().abs()
        RS = Rolling_Up / Rolling_Down
        RSI = 100.0 - (100.0 / (1.0 + RS))

        self.df = self.df.join(pd.Series(RSI, name='RSI_' + str(n)))

        return self.df

    def weighted_moving_average(self, n, weights):
        """Calculate weighted moving average
        :param n: time period
        :param weights: numpy vector of weights, must be of length n
        :return: pandas.DataFrame
        """
        if n != weights.size:
            raise Exception("Weights vector must be of same length as window")

        sum_weights = np.sum(weights)
        weighted_ma = (self.df['Close']
                       .rolling(window=n, center=True)
                       .apply(lambda x: np.sum(weights * x) / sum_weights, raw=False)
                       )
        self.df = self.df.join(pd.Series(weighted_ma, name='WMA_' + str(n)))

        return self.df
