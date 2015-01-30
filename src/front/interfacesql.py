#!/usr/bin/python

"""
HDF5/SQLite Interface

Copyright (C) 2014 by Andrew Chalres Hawkins

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

""" Import Declarations """
import h5py
import subprocess as sp
import sqlite3

""" Constant Declarations """
DATA = "../../data/"
REFERENCE = DATA + "reference.h5"
MASTER = DATA + "master.db"
DATA_TYPE = h5py.special_dtype(vlen=bytes)

""" Main Functions """
""" Manipulate Internal Tiers """
def getTiers():
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Extract the tiers.
    tiers = [tier for tier in fid["internal"]]

    # Close the reference file.
    fid.close()

    return tiers

def addTier(tier):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Check if the tier already exists, if so close and return false.
    if fid["internal"].__contains__(tier):
        fid.close()
        return False

    # Add the tier to the group.
    fid["internal"].create_dataset(tier, ())

    # Close the reference file.
    fid.close()

    return True

def removeTier(tier):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Check if the tier already exists, if not close and return false.
    if not fid["internal"].__contains__(tier):
        fid.close()
        return False

    # Remove the tier from the group.
    del fid["internal"][tier]

    # Close the reference file.
    fid.close()

    return True

""" Manipulate Internal Tier Lists """
def getTierList(tier, decode=True):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Check if values have been defined yet, if not close and return an empty
    # array.
    if fid["internal"][tier].shape == ():
        fid.close()
        return []

    # Extract the items in the given tier.
    items = []
    if decode:
        items = [item.decode() for item in fid["internal"][tier]]
    else:
        items = [item for item in fid["internal"][tier]]

    # Close the reference file.
    fid.close()

    return items

def addToTierList(tier, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Encode the input item.
    item = item.encode()

    # Get the current list of items.
    items = getTierList(tier, False)

    # Check if the item has already been added, if so close and return false.
    if item in items:
        fid.close()
        return False

    # Add the new item to the list.
    items.append(item)

    # Remove the old list.
    del fid["internal"][tier]

    # Add the new list.
    fid["internal"].create_dataset(tier, dtype=DATA_TYPE, data=items)

    # Close the reference file.
    fid.close()

    return True

def removeFromTierList(tier, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Encode the input item.
    item = item.encode()

    # Get the current list of items.
    items = getTierList(tier, False)

    # Check if the item is in the tier, if not close and return false.
    if item not in items:
        fid.close()
        return False

    # Remove the item from the list.
    items.remove(item)

    # Remove the old list.
    del fid["internal"][tier]

    # Add the new list.
    if len(items) == 0:
        fid["internal"].create_dataset(tier, ())
    else:
        fid["internal"].create_dataset(tier, dtype=DATA_TYPE, data=items)

    # Close the reference file.
    fid.close()

    return True

""" Manipulate External Variables """
def getVariables():
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Extract the tiers.
    variables = [variable for variable in fid["external"]]

    # Close the reference file.
    fid.close()

    return variables

def addVariable(variable):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Check if the variable already exists, if so close and return false.
    if fid["external"].__contains__(variable):
        fid.close()
        return False

    # Add the variable to the group.
    fid["external"].create_dataset(variable, ())

    # Close the reference file.
    fid.close()

    return True

def removeVariable(variable):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Check if the variable already exists, if not close and return false.
    if not fid["external"].__contains__(variable):
        fid.close()
        return False

    # Remove the variable from the group.
    del fid["external"][variable]

    # Close the reference file.
    fid.close()

    return True


""" Manipulate External Variable Lists """
def getVariableList(variable, decode=True):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Check if values have been defined yet, if so close and return false.
    if fid["external"][variable].shape == ():
        fid.close()
        return []

    # Extract the items in the given variable.
    if decode:
        items = [item.decode() for item in fid["external"][variable]]
    else:
        items = [item for item in fid["external"][variable]]

    # Close the reference file.
    fid.close()

    return items

def getVariableHash():
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Get the external group.
    external = fid["external"]

    # Iterate over the external group and match possible inputs with known
    # variables.
    match = dict()
    for value in external:
        if external[value].shape != () or value != "Missing":
            for key in external[value]:
                match[key.decode()] = value

    # Close the reference file.
    fid.close()

    return match

def getDateFormats():
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Extract the date formats without the leading '$'.
    dates = [entry.decode()[1:] for entry in fid["external"]["Date"] if
        entry.decode()[0] == '$']

    # Close the reference file.
    fid.close()

    return dates

def addToVariableList(variable, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Convert to lowercase and encode the input item.
    item = item.lower().encode()

    # Get the current list of items.
    items = getVariableList(variable, False)

    # Check if the item has already been added, if so close and return false.
    if item in items:
        fid.close()
        return False

    # Add the new item to the list.
    items.append(item)

    # Remove the old list.
    del fid["external"][variable]

    # Add the new list.
    fid["external"].create_dataset(variable, dtype=DATA_TYPE, data=items)

    # Close the reference file.
    fid.close()

    return True

def removeFromVariableList(variable, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Convert to lowercase and encode the input item.
    item = item.lower().encode()

    # Get the current list of items.
    items = getVariableList(variable, False)

    # Check if the item is in the variable, if not close and return false.
    if item not in items:
        fid.close()
        return False

    # Remove the item from the list.
    items.remove(item)

    # Remove the old list.
    del fid["external"][variable]

    # Add the new list.
    if len(items) == 0:
        fid["external"].create_dataset(variable, ())
    else:
        fid["external"].create_dataset(variable, dtype=DATA_TYPE, data=items)

    # Close the reference file.
    fid.close()

    return True

""" Manipulate Product Data """
def getMatch(element, decode=True):
    """
    """

    # Open the master database.
    connection = sqlite3.connect(MASTER)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve all items under element.
    products = []
    for row in cursor.execute("""SELECT ({col}) FROM info;""".
        format(col=element)):
        products.append(row[0])

    # Close the cursor.
    cursor.close()

    # Close the connection.
    connection.close()

    return products

def getAllProducts():
    """
    """

    # Open the master database.
    connection = sqlite3.connect(MASTER)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve the product's information.
    cursor.execute("""SELECT product, sku, account, class, category, 
subcategory FROM info;""")

    # Fetch the first respnded row.
    productData = cursor.fetchall()

    return productData

def getProduct(product):
    """
    """

    # Open the master database.
    connection = sqlite3.connect(MASTER)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the statement to retrieve the product's information.
    cursor.execute("""SELECT * FROM info WHERE product='{prod}';""".
        format(prod=product))

    # Fetch the first respnded row.
    productData = cursor.fetchone()

    return productData

def addProduct(productData):
    """
    productData (tuple): Must be of the form (product, sku, account, class,
        category, subcategory)
    """

    # Open the master database.
    connection = sqlite3.connect(MASTER)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to write the new data to the database.
    cursor.execute("""INSERT INTO info (product, sku, account, class, 
category, subcategory) VALUES (?, ?, ?, ?, ?, ?)""", productData)

    # Commit the change to the database.
    connection.commit()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    connection.close()

    return True

def removeProduct(product):
    """
    """

    # Open the master database.
    connection = sqlite3.connect(MASTER)

    # Create a cursor from the connection.
    cursor = connection.cursor()

    # Execute the command to remove the row of the given product.
    cursor.execute("""DELETE FROM info WHERE product=?""", (product,))

    # Commit the change to the database.
    connection.commit()

    # Close the cursor.
    cursor.close()

    # Close the connection.
    connection.close()

    return True

""" HDF5 Management """
def repackDB():
    """
    """

    # Repack the database.
    sp.call(["h5repack", REFERENCE, DATA + "temp.h5"])

    # Replace the old database with the new, repacked one.
    replaceDB()

    return True

def forgeDB():
    """
    """

    # Copy of the database file.
    sp.call(["cp", REFERENCE, DATA + "temp.h5"])

    return True


def replaceDB():
    """
    """

    # Replace the current database with the inputted one.
    sp.call(["mv", DATA + "temp.h5", REFERENCE])

    return True

def removeDB():
    """
    """

    # Remove the copied database file.
    sp.call(["rm", DATA + "temp.h5"])

    return True

""" Helper Functions """

