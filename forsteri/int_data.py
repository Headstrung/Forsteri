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

def getTempCount(connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Get the variables list.
    variables = getVariables(connection)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the create table statement.
    found = []
    for variable in variables:
        cursor.execute("SELECT product FROM {v} WHERE product LIKE 'TEMP-%'".\
            format(v=variable))
        found.append(cursor.fetchall())

    # Close the cursor.
    cursor.close()

    # Convert to single list.
    found = [int(y[0][5:]) for x in found for y in x]

    # Close the connection.
    if flag:
        connection.close()

    # Determine the count of temporaries.
    if len(found) == 0:
        count = 0
    else:
        count = max(found)

    return count

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

    # 
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
