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

""" Constant Declarations """
REFERENCE = "../../data/reference.h5"

""" Main Functions """
def getTiers():
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, "r")

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
    fid = h5py.File(REFERENCE, "r+")

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
    fid = h5py.File(REFERENCE, "r+")

    # Check if the tier already exists.
    if not fid["internal"].__contains__(tier):
        return False

    # Remove the tier from the group.
    del fid["internal"][tier]

    # Close the reference file.
    fid.close()

    return True

def getList(tier, decode=True):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, "r")

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

def addToList(tier, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, "r+")

    # Encode the input item.
    item = item.encode()

    # Get the current list of items.
    items = getList(tier, False)

    # Check if the item has already been added.
    if item in items:
        return False

    # Add the new item to the list.
    items.append(item)

    # Remove the old list.
    del fid["internal"][tier]

    # Add the new list.
    fid["internal"].create_dataset(tier, dtype="S100", data=items)

    # Close the reference file.
    fid.close()

    return True

def removeFromList(tier, item):
    """
    """

    # Open the reference file.
    fid = h5py.File(REFERENCE, "r+")

    # Encode the input item.
    item = item.encode()

    # Get the current list of items.
    items = getList(tier, False)

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
        fid["internal"].create_dataset(tier, dtype="S100", data=items)

    # Close the reference file.
    fid.close()

    return True

""" Helper Functions """

