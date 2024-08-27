from collections import namedtuple
import numpy as np

FigAx = namedtuple("Subplots", ["fig", "ax"])

def circular_hist(ax, x, bins=16, density=True, offset=0, gaps=True):
    """
    Produce a circular histogram of angles on ax.
    - ax should be set to polar projection!!
    - density=True is *highly* recommended, since human brains process the "magnitude"
        of a segment as its area, rather than its radius. Because of this,
        density=False is prone to misleading readers.

    Courtesy of user jwalton on StackOverflow
    https://stackoverflow.com/questions/22562364/circular-polar-histogram-in-python

    Parameters
    ----------
    ax : matplotlib.axes._subplots.PolarAxesSubplot
        axis instance created with subplot_kw=dict(projection='polar').

    x : array
        Angles to plot, expected in units of radians.

    bins : int, optional
        Defines the number of equal-width bins in the range. The default is 16.

    density : bool, optional
        If True plot frequency proportional to area. If False plot frequency
        proportional to radius. The default is True.

    offset : float, optional
        Sets the offset for the location of the 0 direction in units of
        radians. The default is 0.

    gaps : bool, optional
        Whether to allow gaps between bins. When gaps = False the bins are
        forced to partition the entire [-pi, pi] range. The default is True.

    Returns
    -------
    n : array or list of arrays
        The number of values in each bin.

    bins : array
        The edges of the bins.

    patches : `.BarContainer` or list of a single `.Polygon`
        Container of individual artists used to create the histogram
        or list of such containers if there are multiple input datasets.
    """
    # Wrap angles to [-pi, pi)
    x = (x + np.pi) % (2 * np.pi) - np.pi

    # Force bins to partition entire circle
    if not gaps:
        bins = np.linspace(-np.pi, np.pi, num=bins + 1)

    # Bin data and record counts
    n, bins = np.histogram(x, bins=bins)

    # Compute width of each bin
    widths = np.diff(bins)

    # By default plot frequency proportional to area
    if density:
        # Area to assign each bin
        area = n / x.size
        # Calculate corresponding bin radius
        radius = (area / np.pi) ** .5
    # Otherwise plot frequency proportional to radius
    else:
        radius = n

    # Plot data on ax
    patches = ax.bar(bins[:-1], radius, zorder=1, align='edge', width=widths,
                     edgecolor='C0', fill=True, linewidth=1)

    # Set the direction of the zero angle
    ax.set_theta_offset(offset)

    # Remove ylabels for area plots (they are mostly obstructive)
    if density:
        ax.set_yticks([])

    return n, bins, patches


def spray_plot(ax, angles):
    """
    Plot spray angles as a circular histogram on ax.
    :param ax: matplotlib.axes._subplots.PolarAxesSubplot
        axis instance created with subplot_kw=dict(projection='polar').
    :param angles: list, np.ndarray, pd.Series of angles (in degrees)
    :return: None
    """
    circular_hist(ax, np.deg2rad(angles), bins=16, offset=np.pi/2, gaps=False)
    ax.set_xticks(np.pi / 180. * np.linspace(180, -180, 16, endpoint=False))
    ax.set_xlim(-np.pi / 2, np.pi / 2)


def launch_plot(ax, angles):
    """
    Plot launch angles as a circular histogram on ax.
    :param ax: matplotlib.axes._subplots.PolarAxesSubplot
        axis instance created with subplot_kw=dict(projection='polar').
    :param angles: list, np.ndarray, pd.Series of angles (in degrees)
    :return: None
    """
    circular_hist(ax, np.deg2rad(angles), bins=12, gaps=False)
    ax.set_xticks(np.pi / 180. * np.linspace(180, -180, 12, endpoint=False))
    ax.set_xlim(-np.pi / 2, np.pi / 2)
