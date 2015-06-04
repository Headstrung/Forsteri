#!/usr/bin/python

"""
SQLite Database Interface for Data

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
import datetime as dt
import os
import sqlite3
import sys

"""
Constant Declarations
"""
if os.name == "nt":
    DATA = "J:\\"
elif os.name == "posix":
    DATA = "/mnt/forecastdb/"
MASTER = ''.join([DATA, "data.db"])

"""
Managing Relations
"""
def addVariable(variable, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the add column statement.
    cursor.execute("""CREATE TABLE IF NOT EXISTS "{v}" (
                        `date` TEXT NOT NULL,
                        `product` TEXT,
                        `value` REAL,
                        UNIQUE (`date`, `product`)
);""".format(v=variable))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeVariable(variable, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Remove the table from the database.
    cursor.execute("""DROP TABLE IF EXISTS {v}""".format(v=variable))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getVariables(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the create table statement.
    cursor.execute("""SELECT name FROM sqlite_master WHERE type='table';""")

    # Fetch the returned values.
    variables = [variable[0] for variable in cursor.fetchall()]

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return variables

def hasVariables(product, convert=False, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Get the list of variables.
    variables = getVariables(connection)

    # Initialize the list of had variables.
    hasVariables = []

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the list of variables.
    for variable in variables:
        cursor.execute("""SELECT product FROM {v} WHERE product='{p}'""".\
            format(v=variable, p=product))
        if cursor.fetchone() is not None:
            hasVariables.append(variable)

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    # Convert if that flag has been given.
    if convert:
        hasVariables = [fromSQLName(x) for x in hasVariables]

    return hasVariables

def latestData(product, variables, convert=False, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Convert the values to SQL names if needed.
    if convert:
        variables = [toSQLName(variable) for variable in variables]

    # Initialize the latest list.
    latest = []

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over the input variables.
    for variable in variables:
        cursor.execute("""SELECT MAX(date) FROM {v} WHERE product='{p}'""".\
            format(v=variable, p=product))
        latest.append(cursor.fetchone()[0])

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return latest

def obsCount(product, variables, convert=False, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Convert the values to SQL names if needed.
    if convert:
        variables = [toSQLName(variable) for variable in variables]

    # Initialize the count list.
    count = []

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # 
    for variable in variables:
        cursor.execute("""SELECT COUNT(value) FROM {v} WHERE product='{p}'""".\
            format(v=variable, p=product))
        count.append(cursor.fetchone()[0])

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return count

"""
Managing Data
"""
def addData(variable, data, overwrite=False, connection=None):
    """
    data (list): (date, product, value)
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create the data string
    dataStr = ''.join(["('", str(data[0]), "', '", str(data[1]), "', ",
        str(data[2]), ')'])

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Insert the new data into the database.
    if overwrite:
        cursor.execute("""INSERT OR REPLACE INTO {v} VALUES {d}""".\
            format(v=variable, d=dataStr))
    else:
        cursor.execute("""INSERT OR IGNORE INTO {v} VALUES {d}""".\
            format(v=variable, d=dataStr))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getData(product, variable, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the satement to pull all date and value data.
    cursor.execute("""SELECT date, value FROM {v} WHERE product='{p}' ORDER BY
date""".format(v=variable, p=product))

    # Fetch the returned values.
    data = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return data

def getAllData(product, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Get the variables that exist for the product.
    variables = hasVariables(product)

    # Remove nonmonthly variables.
    variables = [variable for variable in variables if variable[-8:] ==\
        "_monthly"]

    # Check for finished goods monthly.
    if "finished_goods_monthly" not in variables:
        #print("Finished goods monthly was not found in the database.")
        return None, None

    # Create the repeated strings.
    select = "finished_goods_monthly.date, finished_goods_monthly.value, "
    joins = ""
    inj = " INNER JOIN "
    dte = ".date"
    pdt = ".product"
    fgd = "finished_goods_monthly.date="
    fgp = "finished_goods_monthly.product="

    # Create header information.
    header = ["date", "finished_goods_monthly"]

    # Iterate over the variables and create the string.
    for variable in variables:
        if variable != "finished_goods_monthly":
            select = select + variable + ".value, "
            joins = joins + inj + variable + " ON " + fgd + variable + dte +\
                " AND " + fgp + variable + pdt
            header.append(variable)

    select = select[0 : len(select) - 2]

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to get the data.
    cursor.execute("""SELECT {s} FROM finished_goods_monthly{j} WHERE 
finished_goods_monthly.product='{p}'""".format(s=select, j=joins, p=product))

    # Fetch all data.
    data = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    # Encode all strings.
    header = [x.encode() for x in header]
    data2 = []
    for y in data:
        temp = [y[0].encode()]
        temp.extend(y[1:])
        data2.append(tuple(temp))

    return header, data2

def updateForecast(product, method, forecast, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Find today's date.
    today = dt.date(1, 1, 1).today()

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to insert the data into the database.
    for month in range(0 ,12):
        if month + 1 > today.month:
            date = dt.date(today.year, month + 1, 1)
        else:
            date = dt.date(today.year + 1, month + 1, 1)
        try:
            cursor.execute("""INSERT INTO forecast (date, product) VALUES
('{d}', '{p}')""".format(d=date, p=product))
        except sqlite3.IntegrityError:
            pass
        cursor.execute("""UPDATE forecast SET {m}={f} WHERE
date='{d}' AND product='{p}'""".format(m=method, f=forecast[month], d=date,
    p=product))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getForecast(product, method=None, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # If a method is given, get only its data.
    if method:
        cursor.execute("""SELECT date, {m} FROM forecast WHERE product='{p}'
ORDER BY date""".format(m=method, p=product))
    else:
        cursor.execute("""SELECT date, mlr, ema, arma, aux FROM forecast WHERE
product='{p}' ORDER BY date""".format(p=product))

    # Fetch the forecast values.
    forecast = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    # Create the final list.
    final = dict()

    # Iterate over all rows and find the first non nan value.
    for row in forecast:
        for i in range(1, len(row)):
            if row[i] is not None:
                final[dt.datetime.strptime(row[0], "%Y-%m-%d")] = row[i]
                break

    return final

def changeName(oldName, newName, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Get the list of variables for the product.
    variables = hasVariables(oldName, False, connection)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Iterate over all of the variables that contain the product.
    for variable in variables:
        cursor.execute("""UPDATE {v} SET product='{nn}' WHERE
product='{ol}'""".format(v=variable, ol=oldName, nn=newName))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def trimLeadingZeros(variable, connection=None):
    """
    Remove any leading in time zeros.

    Args:
      variable (str): The variable to be rediscretized.
      connection (sqlite3.Connection, optional): A connection to the database.

    Returns:
      bool: True if sucessful, false otherwise.
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create the cursors from the connection.
    cursor1 = connection.cursor()
    cursor2 = connection.cursor()

    # Get a list of the products in the variable.
    cursor1.execute("""SELECT DISTINCT(product) FROM {v}""".format(v=variable))

    # Iterate over the returned products.
    for product in cursor1.fetchall():
        cursor2.execute("""SELECT date, value FROM {v} WHERE product='{p}' 
ORDER BY date""".format(v=variable, p=product[0]))

        # Iterate over the returned data.
        for element in cursor2.fetchall():
            if element[1] == 0:
                cursor2.execute("""DELETE FROM {v} WHERE date='{d}' AND 
product='{p}'""".format(v=variable, d=element[0], p=product[0]))
            else:
                break

    # Close the cursors.
    cursor1.close()
    cursor2.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def rediscretize(variable, method="sum", connection=None):
    """
    Rediscretize a variable's data to be monthly.

    Args:
      variable (str): The variable to be rediscretized.
      connection (sqlite3.Connection, optional): A connection to the database.
    """

    # Create the name of the monthly table.
    variableRe = variable + "_monthly"

    # Create the variable table if it does not already exist.
    addVariable(variableRe, connection)

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to rediscretize to monthly.
    if method == "singular":
        cursor.execute("""INSERT OR REPLACE INTO {vr} (date, product, value)
SELECT strftime('%Y-%m-01', date), product, value FROM {v} GROUP BY product,
strftime('%Y-%m', date) ORDER BY product;""".format(vr=variableRe,
            v=variable))
    elif method == "sum":
        cursor.execute("""INSERT OR REPLACE INTO {vr} (date, product, value)
SELECT strftime('%Y-%m-01', date), product, sum(value) FROM {v} GROUP BY
product, strftime('%Y-%m', date) ORDER BY product;""".format(vr=variableRe,
            v=variable))
    elif method == "average":
        cursor.execute("""INSERT OR REPLACE INTO {vr} (date, product, value)
SELECT strftime('%Y-%m-01', date), product, avg(value) FROM {v} GROUP BY
product, strftime('%Y-%m', date) ORDER BY product;""".format(vr=variableRe,
            v=variable))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

"""
Error
"""
def updateError(meth="mlr", connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Get the error values.
    cursor.execute("""SELECT fg.date, fg.product, fg.value-forecast.{m} FROM
finished_goods_monthly AS fg INNER JOIN forecast ON fg.date=forecast.date AND
fg.product=forecast.product""".format(m=meth))

    # Fetch the error data.
    errors = cursor.fetchall()

    # Iterate over all months and products and update the error values.
    for error in errors:
        if error[2] is None:
            continue
        cursor.execute("""UPDATE forecast SET {m}_error={e} WHERE date='{d}'
AND product='{p}'""".format(m=meth, e=error[2], d=error[0], p=error[1]))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

"""
Linking
"""
def linkData(old, new, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Get the variables assigned to the old product.
    variables = hasVariables(new)
    variables = [x for x in variables if x[-8:] != "_monthly"]
    variables.remove("forecast")

    # Iterate over the variables.
    for variable in variables:
        # Get the earliest date from the new product.
        cursor.execute("""SELECT MIN(date) FROM {v} WHERE product='{n}'""".\
            format(v=variable, n=new))
        firstDate = cursor.fetchone()[0]

        # Get all data from the old product before the first date.
        cursor.execute("""SELECT date, value FROM {v} WHERE product='{o}' AND
date<'{d}' ORDER BY date""".format(v=variable, o=old, d=firstDate))
        dataTemp = cursor.fetchall()

        # Iterate over the values that were pulled from the old product.
        for point in dataTemp:
            cursor.execute("""INSERT INTO {v} (date, product, value) VALUES
('{d}', '{n}', {val})""".format(v=variable, d=point[0], n=new, val=point[1]))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def unlinkData(old, new, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Get the variables assigned to the old product.
    variables = hasVariables(new)
    variables = [x for x in variables if x[-8:] != "_monthly"]
    variables.remove("forecast")

    # Iterate over the variables.
    for variable in variables:
        # Get the data for the old product.
        cursor.execute("""SELECT date, value FROM {v} WHERE product='{o}'""".\
            format(v=variable, o=old))
        oldData = cursor.fetchall()

        # Iterate over the old data.
        for point in oldData:
            cursor.execute("""DELETE FROM {v} WHERE date='{d}' AND
product='{n}' AND value={val}""".format(v=variable, d=point[0], n=new,
    val=point[1]))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

"""
Helper/Utility Functions
"""
def systematize():
    """
    """

    # Open a connection to the data database.
    connection = sqlite3.connect(MASTER)

    # Get a list of all variables.
    variables = getVariables(connection)

    # Only operate on non monthly data.
    variablesNM = [x for x in variables if x[-8:] != "_monthly"]

    # Remove forecast from the list.
    variablesNM.remove("forecast")

    # Create a list of singular variables.
    singular = ["balance_on_order", "instock_store_count",
        "need_for_target_inventory_level", "store_balance_on_hand",
        "target_inventory_level", "aim_store_count", "balance_on_hand"]

    # Iterate over the variables performing operations on each.
    for variable in variablesNM:
        trimLeadingZeros(variable, connection=connection)
        if variable in singular:
            rediscretize(variable, method="singular", connection=connection)
        else:
            rediscretize(variable, connection=connection)

    # Close and commit the connection.
    connection.commit()
    connection.close()

    print("Systematize complete!")

def toSQLName(text):
    """
    """

    return text.replace(' ', '_').lower()

def fromSQLName(text):
    """
    """

    return text.replace('_', ' ').title()
