#!/usr/bin/python

"""


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
import csv
import datetime as dt
import interface as iface

""" Constant Declarations """


""" Main Functions """
def decompose(source):
    """
    The point of the decompose function is to take a file with an arbitrary
    header and extract only relevent information, based on associations with a
    database.
    """

    # Initialize the data list.
    data = []

    # Open the file and extract the data.
    with open(source, newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='|')
        for row in reader:
            data.append(row)

    # Separate the header.
    header = data[0]

    # Get the variable hash table.
    varHash = iface.getVariableHash()

    # Iterate over the header matching its titles to known variables.
    match = []
    remove = []
    index = 0
    for col in header:
        col = col.lower()
        # If the column item is in the keys list, match the variable.
        try:
            variable = varHash[col]
            match.append(variable)

            # If the variable is Ignore add the index to the remove list.
            if variable == "Ignore":
                remove.append(index)
        # If not, add the title to the Missing variable list and the index to
        # the remove list.
        except KeyError:
            match.append("Missing")
            iface.addToVariableList("Missing", col)
            remove.append(index)

        # Increment the index.
        index += 1

    # Recombine the matched header with data.
    data[0] = match

    # Remove any column that was labeled Ignore or Missing.
    remove = sorted(remove, reverse=True)
    for row in data:
        for i in remove:
            del row[i]

    # Open the file and write the data.
    with open(source + "new", 'w', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)

    return True

""" Helper Functions """
