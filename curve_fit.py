import numpy as np

from scipy.stats import ks_2samp

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import make_pipeline


def median_trend(x, y, n_points_per_bar=10):

    # Function will return None if it is not possible to split the
    # arrays into bars such that:
    #   - the first and last bar have the same number of points,
    #   which is either n_points_per_bar or n_points_per_bar-1
    #   - the difference in number of points between any two bars is at
    #   most 1
    #
    # First, try to split the array so that the number of points in the
    # bars at the ends is n_points_per_bar, and decreasing the number of
    # points in the bars in the middle.
    #   If that does not work, set the number of points in the bars at the
    # ends to n_points_per_bar-1, and try increasing the number of points
    # in the bars in the middle.

    # Compute number of bars and the number of bars that will have
    # n_points_per_bar - 1 points:
    n_bars = x.size // n_points_per_bar + (x.size % n_points_per_bar > 0)
    n_alt_bars = (n_points_per_bar - x.size % n_points_per_bar) \
                 % n_points_per_bar
    alternation = -1

#    print("# bars:", n_bars)
#    print("# altered bars:",n_alt_bars)
    if n_bars - 2 < n_alt_bars:
#        print("trying smaller bars at ends")
        alternation = 1
        n_points_per_bar -= 1
        # Compute number of bars and the number of bars that will have
        # n_points_per_bar + 1 points:
        n_bars = x.size // n_points_per_bar
        n_alt_bars = x.size % n_points_per_bar
#        print("# bars:", n_bars)
#        print("# altered bars:", n_alt_bars)
        if n_bars - 2 < n_alt_bars:
#            print("nope")
            return None

    # Sort by x:
    argsort = np.argsort(x)
    x = x[argsort]
    y = y[argsort]

    medianx = np.zeros(n_bars)
    mediany = np.zeros(n_bars)

    # Iterate over bars and compute median for each of the, keeping
    # track of the index of the lower side of the bar:
    index = 0
    for i_bar in range(n_bars):
        down = index

        # Alter the size of bars in the middle to fit the bars to the
        # array:
        if i_bar > 0 and i_bar <= n_alt_bars:
            up = index + n_points_per_bar + alternation
        else:
            up = index + n_points_per_bar

#        print(down, up)
        medianx[i_bar] = np.median(x[down:up])
        mediany[i_bar] = np.median(y[down:up])
        index = up

    return medianx, mediany


def median_trend_by_n_bars(x, y, n_bars):
    if x.size > n_bars:
        # Sort by x:
        argsort = np.argsort(x)
        x = x[argsort]; y = y[argsort]

        n_over = x.size % n_bars
        medianx = np.zeros(n_bars)
        mediany = np.zeros(n_bars)

        bar_size = x.size // n_bars
        for i in range(n_bars):
            if n_over < n_bars - 1:
                if i > 0 and i <= n_over:
                    down = i * bar_size
                    up = (i + 1) * bar_size + 1
                else:
                    down = i * bar_size
                    up = (i + 1) * bar_size
            else:
                if i == 1:
                    down = i * bar_size
                    up = (i + 1) * bar_size
                else:
                    down = i * bar_size
                    up = (i + 1) * bar_size + 1

            medianx[i] = np.median(x[down:up])
            mediany[i] = np.median(y[down:up])

        return medianx, mediany


def PolynomialRegression(degree=2, **kwargs):
    return make_pipeline(PolynomialFeatures(degree), \
                         LinearRegression(**kwargs))


def poly_fit(x, y, max_deg=4):
    # Set parameter space:
    param_grid = {'polynomialfeatures__degree': np.arange(20),
                  'linearregression__fit_intercept': [True, False],
                  'linearregression__normalize': [True, False]}

    # Split to test and training:
    test_size = 0.3
    x_train, x_test, y_train, y_test = train_test_split(x, y, \
                                                        test_size=test_size)

    # Find best parameter values:
    clf = GridSearchCV(PolynomialRegression(), param_grid, cv=5)
    clf.fit(x_train.reshape(-1, 1), y_train)
    train_err = clf.best_score_
    test_err = clf.score(x_test.reshape(-1, 1), y_test)

    # Construct model curve:
    model = clf.best_estimator_
    print(model)
    xfit = np.linspace(min(x), max(x), 10000)
    yfit = model.fit(x.reshape(-1, 1), y).predict(xfit.reshape(-1, 1))

    return xfit, yfit, train_err, test_err
