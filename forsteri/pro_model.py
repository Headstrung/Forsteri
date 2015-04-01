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
        products = isql.getProductNames()

    # Iterate over each product.
    for product in products:
        # Get the data for the product.
        data = idata.getData(product, "finished_goods", connection)

        # If no data is held for a product skip it.
        if len(data) == 0:
            continue

        # Convert the data to an overlapped numpy array.
        data = overlap(data)

        # Find the averages for each month.
        average = eMA(data, alpha=0.7)

        # Convert nan to NULL.
        average = ["NULL" if np.isnan(x) else x for x in average]

        # Add the forecasts to the database.
        idata.updateForecast(product, "ema", average, connection)

    # Commit and close the connection.
    connection.commit()
    connection.close()

    return True

def runMLR(products=None):
    """
    Run the multiple linear regression model for the given products with all
    available variables.
    """

    # Open a connection to the data database.
    connection = sqlite3.connect(idata.MASTER)

    # Get all products if none are given.
    if products is None:
        products = isql.getProductNames()

    # Iterate over each product.
    for product in products:
        print(product)
        # Get the data for the current product.
        (header, data) = idata.getAllData(product)

        # If there is no data for a product, skip to the next product.
        if data is None:
            continue

        # Process the data into a the overlap form.
        dataNew = overlap3(data)

        # Iterate over each month.
        forecast = []
        for i in range(0, 12):
            try:
                # Determine the coefficient values
                (beta, fit) = mLR(dataNew[i][:, 0], dataNew[i][:, 1:])

                # Determine the values to use for each variable.
                vals = np.concatenate((np.array([1]), eMA(dataNew[i][:, 1:])))

                # Find the forecast.
                forecast.append(np.dot(vals, beta))
            except IndexError:
                # Add nan to the forecast.
                forecast.append(np.nan)

        # Concert nan to NULL.
        forecast = ["NULL" if np.isnan(x) else x for x in forecast]

        # Add the forecast values to the database.
        idata.updateForecast(product, "mlr", forecast, connection)

    # Commit and close the connection.
    connection.commit()
    connection.close()

    return True

"""
Model Functions
"""
def eMA(data, alpha=None):
    """
    Find the exponential moving average of some data.

    Args:
      data (numpy.array): An array of data.
      alpha (int, optional): The weighting factor.

    Returns:
      numpy.array: 
    """

    # Find the shape of the input data.
    shape = np.shape(data)

    # If the dimension is higher than one run the function recursively.
    if len(shape) == 2:
        average = []
        for i in range(0, shape[1]):
            average.append(eMA([x[i] for x in data], alpha))
        return average
    elif len(shape) > 2:
        raise(IndexError("this function can only take up to a 2 dimensional \
array"))

    # If no alpha is given determine the alpha.
    if alpha is None:
        alpha = 2 / (len(data) + 1)

    # Find the compliment of alpha.
    comp = 1 - alpha

    # Find the first non nan index.
    try:
        index = np.where(np.isnan(data) == False)[0][0]
    except IndexError:
        return data[-1]

    # Set the initial average.
    average = data[index]

    # Iterate over all data points and update the average.
    for i in range(index + 1, len(data)):
        # If the value is nan then do not change the average.
        if np.isnan(data[i]):
            pass
        else:
            average = comp * average + alpha * data[i]

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

    # Determine the historical fit of data.
    fit = np.dot(indB, beta)

    return beta, fit

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

    # If the first month is not one, add dates.
    if firstMonth != 1:
        temp = [(str(dt.date(firstYear, i, 1)), np.nan) for i in range(1,
            firstMonth)]
        temp.extend(data2)
        data2 = temp.copy()

    # If the last month is not 12, add dates.
    if lastMonth != 12:
        data2.extend([(str(dt.date(lastYear, i, 1)), np.nan) for i in \
            range(lastMonth + 1, 13)])

    # Extract only the values from the data.
    values = [x[1] for x in data2]

    # Reshape the data.
    new = np.array([values[i : i + 12] for i in range(0, len(values), 12)])

    return new

def overlap2(data):
    """
    """

    # Make a copy of the data.
    data2 = data.copy()

    # Extract the first and last year and month.
    firstYear = int(data2[0][0][0 : 4])
    firstMonth = int(data2[0][0][5 : 7])
    lastYear = int(data2[-1][0][0 : 4])
    lastMonth = int(data2[-1][0][5 : 7])

    naTemp = [np.nan] * (len(data2[0]) - 1)

    # If the first month is not one, add dates with nan values.
    if firstMonth != 1:
        head = []
        for i in range(1, firstMonth):
            temp = [str(dt.date(firstYear, i, 1))]
            temp.extend(naTemp)
            head.append(tuple(temp))
        head.extend(data2)
        data2 = head.copy()

    # If the last month is not 12, add dates with nan values.
    if lastMonth != 12:
        tail = []
        for i in range(lastMonth + 1, 13):
            temp = [str(dt.date(lastYear, i, 1))]
            temp.extend(naTemp)
            tail.append(tuple(temp))
        data2.extend(tail)

    final = [[] for i in range(0, 12)]
    index = 1
    for x in data2:
        final[index % 12].append(x[1:])
        index += 1

    return final

def overlap3(data):
    """
    """

    #
    dataC = data.copy()

    temp = [[] for i in range(0, 12)]

    index = int(dataC[0][0][5 : 7])
    for x in dataC:
        temp[(index % 12) - 1].append(x[1:])
        index += 1

    final = []
    for x in temp:
        final.append(np.array(x))

    return final

def curtail(data):
    """
    """

    # Make a copy of the data.
    variables = data.copy()

    # Find all of the start and end dates.
    starts = []
    ends = []
    for variable in variables.values():
        starts.append(variable[0][0])
        ends.append(variable[-1][0])

    # Determine the latest start and the earliest end.
    first = max(starts)
    last = min(ends)

    # Extract the data.
    newData = dict()
    for (key, value) in variables.items():
        temp = []
        for point in value:
            if point[0] < first or point[0] > last:
                pass
            else:
                temp.append(point)
        newData[key] = temp

    return newData

def separate(data):
    """
    """

    # 
    for (key, value) in data.items():
        for i in range(0, 12):
            months[i + 1] = np.column_stack(months[i + 1], )






