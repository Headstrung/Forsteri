#!/usr/bin/python

"""
SQLite Database Interface for Data

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
import sqlite3

"""
Constant Declarations
"""
DATA = "/home/andrew/Dropbox/product-quest/Forsteri/data/"
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
    variables = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    # Only get the first index of the fetch.
    variables = [variable[0] for variable in variables]

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

"""
Managing Data
"""
def addData(variable, data, connection=None):
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

    # Remove the table from the database.
    cursor.execute("""INSERT OR REPLACE INTO {v} VALUES {d}""".\
        format(v=variable, d=dataStr))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getData(product, variable=None, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    #
    cursor.execute("""""".format())

    #
    data = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return data

def rediscretize(variable, connection=None):
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
    cursor.execute("""INSERT OR REPLACE INTO {vr} (date, product, value) SELECT
strftime('%Y-%m-01', date), product, sum(value) FROM {v} GROUP BY
strftime('%Y-%m', date), product ORDER BY product;""".format(vr=variableRe,
        v=variable))

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
def toSQLName(text):
    """
    """

    return text.replace(' ', '_').lower()

def fromSQLName(text):
    """
    """

    return text.replace('_', ' ').title()
