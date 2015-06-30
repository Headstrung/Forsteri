#!/usr/bin/python

"""
Graphical User Interface

Copyright (c) 2014, 2015 Andrew Hawkins

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
Import Declarations
"""
import copy
import datetime as dt
import numpy as np
import sqlite3
import threading as td
import wx

from forsteri.interface import data as idata
from forsteri.interface import sql as isql

"""
Constant Declarations
"""


"""
Main Functions
"""
def runAllErrors():
    """
    """

    # Create the progress dialog box.
    progress_dlg = wx.ProgressDialog("Running Errors",
        "Opening database connection.")

    # Open a connection to the data database.
    connection = sqlite3.connect(idata.MASTER)

    progress_dlg.Update(10, "Connection initialized, running MLR errors.")

    # Find the MLR errors.
    idata.updateError("mlr", connection)

    progress_dlg.Update(40, "MLR errors complete, running EMA errors.")

    # Find the EMA errors.
    idata.updateError("ema", connection)

    progress_dlg.Update(70, "EMA errors complete, running Naive errors.")

    # Find the Naive errors.
    idata.updateError("naive", connection)

    progress_dlg.Update(99, "Naive errors complete, commiting changes.")

    # Commit and close the connection.
    connection.commit()
    connection.close()

    progress_dlg.Update(100, "Error process complete.")
    progress_dlg.Destroy()

    return True

def runAll(products=None):
    """
    """

    # Create the progress dialog box.
    progress_dlg = wx.ProgressDialog("Running Models",
        "Opening database connection.", wx.PD_CAN_ABORT|wx.PD_ELAPSED_TIME|
        wx.PD_REMAINING_TIME)

    # Open a connection to the data database.
    connection = sqlite3.connect(idata.MASTER)

    progress_dlg.Update(5, "Connection initialized, gathering products.")

    # Get all products if none are given.
    if products is None:
        products = isql.getProductNames()

    progress_dlg.Update(10, "Products gathered, running EMA model.")

    # Run the EMA model.
    runEMA(products, connection)

    progress_dlg.Update(40, "EMA model complete, running MLR model.")

    # Run the MLR model.
    runMLR(products, connection)

    progress_dlg.Update(70, "MLR model complete, running Nieve model.")

    # Run the Naive model.
    runNaive(products, connection)

    progress_dlg.Update(99, "All models complete, commiting changes.")

    # Commit and close the connection.
    connection.commit()
    connection.close()

    progress_dlg.Update(100, "Model process complete.")
    progress_dlg.Destroy()

    return True

def runEMA(products=None, connection=None):
    """
    Run the exponential moving avergae model for the given products.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(idata.MASTER)
        flag = True

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

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def runMLR(products=None, connection=None):
    """
    Run the multiple linear regression model for the given products with all
    available variables.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(idata.MASTER)
        flag = True

    # Get all products if none are given.
    if products is None:
        products = isql.getProductNames()

    # Iterate over each product.
    for product in products:
        # Get the data for the current product.
        (header, data) = idata.getAllData(product)

        # If there is no data for a product, skip to the next product.
        if data is None:
            continue

        # Process the data into a the overlap form.
        try:
            dataNew = overlap3(data)
        except IndexError:
            continue

        # Iterate over each month.
        forecast = []
        for i in range(0, 12):
            try:
                # Determine the coefficient values
                (beta, fit) = mLR(dataNew[i][:, 0], dataNew[i][:, 1:])

                # Determine the values to use for each variable.
                vals = np.concatenate((np.array([1]), eMA(dataNew[i][:, 1:],
                    alpha=0.7)))

                # Find the forecast.
                forecast.append(np.dot(vals, beta))
            except IndexError:
                # Add nan to the forecast.
                forecast.append(np.nan)

        # Concert nan to NULL.
        forecast = ["NULL" if np.isnan(x) else x for x in forecast]

        # Add the forecast values to the database.
        idata.updateForecast(product, "mlr", forecast, connection)

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def runNaive(products=None, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(idata.MASTER)
        flag = True

    # Get all products if none are given.
    if products is None:
        products = isql.getProductNames()

    # Get the date.
    today = dt.date(1, 1, 1).today()

    # Get the finished goods data.
    for product in products:
        data = idata.getData(product, "finished_goods_monthly", connection)

        # Extract the last 12 data points.
        forecast = data[-12:]

        # Convert the dates to be just the months.
        forecast = {dt.datetime.strptime(x[0], "%Y-%m-%d").month: x[1] for x\
            in forecast}

        # Pad forecast with NULLs if it is less than length 12.
        if len(forecast) < 12:
            for i in range(1, 13):
                try:
                    forecast[i]
                except KeyError:
                    forecast[i] = "NULL"

        # Sort by month.
        forecast = sorted(forecast.items(), key=lambda s: s[0])

        # Add the forecast values to the database.
        idata.updateForecast(product, "naive", [x[1] for x in forecast],
            connection)

    # Close the connection.
    if flag:
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
        alpha = 2 / (len(data) + 1.0)

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
    data2 = copy.copy(data)

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
        data2 = copy.copy(temp)

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
    data2 = copy.copy(data)

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
    dataC = copy.copy(data)

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
