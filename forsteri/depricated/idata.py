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
DATA = "/home/andrew/Dropbox/product-quest/forsteri/data/"
MASTER = ''.join([DATA, "data.db"])

"""
Product Data
"""
def createProduct(product, connection=None):
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
    cursor.execute("""CREATE TABLE "{p}" (
`date` TEXT NOT NULL UNIQUE,
`forecast` INTEGER,
`finished_goods` INTEGER
);""".format(p=product))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeProduct(product, connection=None):
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
    cursor.execute("""DROP TABLE IF EXISTS "{p}";""".format(p=product))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def getProducts(connection=None):
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
    products = cursor.fetchall()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.close()

    return products

def addVariable(product, variable, connection=None):
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
    cursor.execute("""ALTER TABLE {p} ADD COLUMN {v} REAL""".format(p=product,
        v=variable))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def removeVariable(product, variable, connection=None):
    """
    """

    # Open the master database if it is not supplied.
    flag = False
    if connection is None:
        connection = sqlite3.connect(MASTER)
        flag = True

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Get the list of current attributes.
    cursor.execute("""PRAGMA table_info({p})""".format(p=product))
    attrData = cursor.fetchall()
    attrs = {x[1]: x[2] for x in attrData}
    oAttrs = [y[1] for y in attrData]

    # Remove the input variable.
    del attrs[variable]
    oAttrs.remove(variable)

    # Create the new column list.
    attrStr = ''
    oAttrStr = ''
    for attr in oAttrs:
        attrStr = ''.join([attrStr, "'", attr, "' ", attrs[attr], ', '])
        oAttrStr = ''.join([oAttrStr, attr, ', '])

    attrStr = attrStr[:-2]
    oAttrStr = oAttrStr[:-2]

    # Execute the remove table statements.
    temp = product + "_temp"
    cursor.execute("""ALTER TABLE {p} RENAME TO {t};""".format(p=product,
        t=temp))
    cursor.execute("""CREATE TABLE {p}({a});""".format(p=product, a=attrStr))
    cursor.execute("""INSERT INTO {p}({a}) SELECT {a} FROM {t};""".\
        format(p=product, a=oAttrStr, t=temp))
    cursor.execute("""DROP TABLE {t};""".format(t=temp))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True

def setVariableData(product, variable, data, connection=None):
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
    cursor.execute("""INSERT INTO {p}({v}) """.format(p=product, v=variable))

    # Close the cursor.
    cursor.close()

    # Close the connection.
    if flag:
        connection.commit()
        connection.close()

    return True




