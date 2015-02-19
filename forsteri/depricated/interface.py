#!/usr/bin/python

"""
HDF5 Interface

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
import numpy as np
import subprocess as sp

""" Constant Declarations """
DATA = "../../data/"
REFERENCE = DATA + "reference.h5"
DATA_TYPE = h5py.special_dtype(vlen=bytes)

""" Main Functions """
""" Manipulate Internal Tiers """
def getTiers():
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Extract the tiers.
    tiers = []
    for tier in fid["internal"].keys():
        tiers.append(tier)

    # Close the reference file.
    fid.close()

    return tiers

def addTier(tier):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Check if the tier already exists.
    if fid["internal"].__contains__(tier):
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

    # Check if the tier already exists.
    if not fid["internal"].__contains__(tier):
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

    # Check if values have been defined yet.
    if fid["internal"][tier].shape == ():
        return []

    # Extract the items in the given tier.
    items = []
    if decode:
        for item in fid["internal"][tier]:
            items.append(item.decode())
    else:
        for item in fid["internal"][tier]:
            items.append(item)

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

    # Check if the item has already been added.
    if item in items:
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

    # Check if the item is in the tier.
    if item not in items:
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

    # Check if the variable already exists.
    if fid["external"].__contains__(variable):
        return False

    # Add the tier to the group.
    fid["external"].create_dataset(variable, ())

    # Close the reference file.
    fid.close()

    return True

def removeVariable(variable):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Check if the variable already exists.
    if not fid["external"].__contains__(variable):
        return False

    # Add the tier to the group.
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

    # Check if values have been defined yet.
    if fid["external"][variable].shape == ():
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

    dates = []
    for entry in fid["external"]["Date"]:
        entry = entry.decode()
        if entry[0] == '$':
            dates.append(entry[1:])

    # Close the reference file.
    fid.close()

    return dates

def addToVariableList(variable, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Encode the input item.
    item = item.lower().encode()

    # Get the current list of items.
    items = getVariableList(variable, False)

    # Check if the item has already been added.
    if item in items:
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

    # Encode the input item.
    item = item.encode()

    # Get the current list of items.
    items = getVariableList(variable, False)

    # Check if the item is in the variable.
    if item not in items:
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

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # The groups will always be lower case, so convert.
    element = element.lower()

    # Check if values have been defined yet.
    if fid["match"][element].shape == ():
        return []

    # Extract the list of products.
    products = []
    if decode:
        for product in fid["match"][element]:
            products.append(product.decode())
    else:
        for product in fid["match"][element]:
            products.append(product)

    # Close the reference file.
    fid.close()

    return products

def getProduct(product):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r")

    # Encode the product string.
    product = product.encode()

    # Check if the product has been defined yet.
    if product not in fid["match"]["product"]:
        return ("", "", "", "", "", "")
    else:
        index = 0
        for indv in fid["match"]["product"]:
            if indv == product:
                break
            index += 1

    # Extract the product and its attributes.
    productData = [fid["match"]["product"][index].decode(),
        fid["match"]["sku"][index].decode(),
        fid["match"]["account"][index].decode(),
        fid["match"]["class"][index].decode(),
        fid["match"]["category"][index].decode(),
        fid["match"]["subcategory"][index].decode()]

    # Close the reference file.
    fid.close()

    return productData

def addProduct(product, sku="", account="", className="", category="",
    subcategory=""):
    """
    To Do:
      1) Check if the product has already been added to the DB.
    """

    # Get the dictionary of arguments to inputs.
    args = locals()

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Iterate through the product characteristics.
    for element in fid["match"].keys():
        # Get the data for the element.
        data = getMatch(element, decode=False)

        # Manually select the key when class is the element.
        if element == "class":
            data.append(args["className"].encode())
        else:
            data.append(args[element].encode())

        # Remove the old list.
        del fid["match"][element]

        # Add the new list.
        fid["match"].create_dataset(element, dtype=DATA_TYPE, data=data)

    # Close the reference file.
    fid.close()

    return True

def removeProduct(product):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, mode="r+")

    # Get the list of products.
    products = getMatch("product", decode=False)

    # Encode product for comparisons.
    product = product.encode()

    # Check if the product is defined.
    if product not in products:
        return False

    # Find the index of the product in products.
    index = products.index(product)

    # Remove the product from the list.
    products.pop(index)

    # Remove the old list.
    del fid["match"]["product"]

    # Add the new list.
    if len(products) == 0:
        fid["match"].create_dataset("product", ())
    else:
        fid["match"].create_dataset("product", dtype=DATA_TYPE, data=products)

    # Iterate through the product characteristics.
    for element in fid["match"].keys():
        # Product is already done, so disregard.
        if element != "product":
            # Get the data for the element.
            data = getMatch(element, decode=False)

            # Remove the index from the data.
            data.pop(index)

            # Remove the old list.
            del fid["match"][element]

            # Add the new list.
            if len(data) == 0:
                fid["match"].create_dataset(element, ())
            else:
                fid["match"].create_dataset(element, dtype=DATA_TYPE,
                    data=data)

    # Close the reference file.
    fid.close()

    return True

def setAttribute(product, element, value):
    """
    """

    pass

""" Database Management """
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

