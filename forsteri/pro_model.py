#!/usr/bin/python

"""
Graphical User Interface

Copyright (C) 2014, 2015 by Andrew Chalres Hawkins

This file is part of Forsteri.

Forsteri is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Forsteri is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Forsteri.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Import Declarations
"""
import datetime as dt
import int_data as idata
import int_sql as isql
import numpy as np
import pandas as pd
import scipy as sp
import sqlite3

"""
Constant Declarations
"""


"""
Main Functions
"""
def runEMA(products=None):
    """
    Run the exponential moving avergae model for the given products.
    """

    # Open a connection to the data database.
    connection = sqlite3.connect(idata.MASTER)

    # Get all products if none are given.
    if products is None:
        products = isql.getProductHash().values()

    # Iterate over each product.
    for product in products:
        # Get the data for the product.
        data = idata.getData(product, "finished_goods", connection)

        # Convert the data to an overlapped numpy array.
        data = overlap(data)

        # 
        average = eMA(data, alpha=0.7)

        # 


def runMLR(products=None):
    """
    Run the multiple linear regression model for the given products with all
    available variables.
    """

    # 


"""
Model Functions
"""
def eMA(data, alpha=None):
    """
    Find the exponential moving average of some data.

    Args:
      data (numpy.array): An array of data. If the dimension is 2 the columns
        will be treated as separate variables.
      alpha (int, optional): The weighting factor.

    Returns:
      numpy.array: 
    """

    # If no alpha is given determine the alpha.
    if alpha is None:
        alpha = 2 / (len(data) + 1)

    # Extract the first row to be the start of the average.
    average = data[0]

    # Iterate over the rows in data and determine the average.
    comp = 1 - alpha
    for i in np.arange(1, np.shape(data)[0]):
        average = comp * average + alpha * data[i];

    return average

def mLR(dep, ind):
    """
    """

    # Add a bias column to the independent variables.
    (rows, cols) = np.shape(ind)
    indB = np.ones((rows, cols + 1))
    indB[:, 1:] = ind

    # Determine the weighting coefficients.
    beta = np.dot(np.dot(np.linalg.pinv(np.dot(indB.T, indB)), indB.T), dep)

    return beta

"""
Helper Functions
"""
def overlap(data):
    """
    data is in the form [(date1, value1), (date2, value2), ...]
    """

    # Make a copy of the data.
    data2 = data.copy()

    # Extract the first and last year and month.
    firstYear = int(data2[0][0][0 : 4])
    firstMonth = int(data2[0][0][5 : 7])
    lastYear = int(data2[-1][0][0 : 4])
    lastMonth = int(data2[-1][0][5 : 7])

    # If the first month is not one add dates.
    if firstMonth != 1:
        temp = [(str(dt.date(firstYear, i, 1)), np.nan) for i in range(1,
            firstMonth)]
        temp.extend(data2)
        data2 = temp.copy()

    # If the last month is not 12 add dates.
    if lastMonth != 12:
        data2.extend([(str(dt.date(lastYear, i, 1)), np.nan) for i in \
            range(lastMonth + 1, 13)])

    # Extract only the values from the data.
    values = [x[1] for x in data2]

    # Reshape the data.
    new = np.array([values[i : i + 12] for i in range(0, len(values), 12)])

    return new
