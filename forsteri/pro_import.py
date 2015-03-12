#!/usr/bin/python

"""
Import Module

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
import csv
import datetime as dt
import int_data as idata
import int_sql as isql
from operator import add
import sqlite3

"""
Constant Declarations
"""


"""
Main Functions
"""
def importTimeseries(source, dateFormat, variable, overwrite=False):
    """
    Columns are time.
    """

    # Run the decompose function to get the full data.
    data = decomposeCut(source, dateFormat)

    # Extract the header.
    header = data[0]
    data2 = data[1:]

    # Aggregate repeated products.
    data2 = aggregate(data2)

    # Perform the preinput operations.
    data2 = preimport(data2)

    # Convert the variable name.
    variableName = idata.toSQLName(variable)

    # Open a connection to the data database.
    connection = sqlite3.connect(idata.MASTER)

    # Iterate over the data.
    rows = len(data2)
    cols = len(data2[0])
    for i in range(0, rows):
        prod = data2[i][0]
        for j in range(1, cols):
            idata.addData(variableName, [header[j], prod, data2[i][j]],
                overwrite, connection)

    # Close the connection and commit changes to the data database.
    connection.commit()
    connection.close()

    return True

def importTimeseries2(source, dateFormat, overwrite=False, shift=False):
    """
    There are multiple variables and a single column is time.
    """

    # Run the decompose function to get the full data.
    data = decomposeCut(source, dateFormat, shift)

    # Extract the header.
    header = data[0]
    data2 = data[1:]

    # Extract the dates.
    dateIndex = header.index("Date")
    dates = [checkDate(x[dateIndex], dateFormat) for x in data2]

    # Remove the date column from the header and data.
    del header[dateIndex]
    for row in data2:
        del row[dateIndex]

    # Perform the preinput operations.
    data2 = preimport(data2)

    # Open a connection to the database.
    connection = sqlite3.connect(idata.MASTER)
    cursor = connection.cursor()

    # 
    index1 = 0
    for row in data2:
        product = row[0]
        index2 = 1
        for col in row[1:]:
            idata.addData(idata.toSQLName(header[index2]), [dates[index1],
                product, col], overwrite, connection)
            index2 += 1
        index1 += 1

    # Close the cursor and connection and commit changes.
    cursor.close()
    connection.commit()
    connection.close()

    return True

def importSingleTime(source, date, overwrite=True):
    """
    There are multiple variables and only one time.
    """

    # Run the decompose function to get the full data.
    data = decomposeCut(source, '')

    # Extract the header.
    header = data[0]
    data2 = data[1:]

    # Aggregate repeated products.
    data2 = aggregate(data2)

    # Perform the preinput operations.
    data2 = preimport(data2)

    # Open a connection to the database.
    connection = sqlite3.connect(idata.MASTER)
    cursor = connection.cursor()

    # 
    for row in data2:
        product = row[0]
        index = 1
        for col in row[1:]:
            idata.addData(idata.toSQLName(header[index]), [str(date),
                product, col], overwrite, connection)
            index += 1

    # Close the cursor and connection and commit changes.
    cursor.close()
    connection.commit()
    connection.close()

    return True

def preimport(data):
    """
    """

    # Determine if the input is a sku.
    try:
        int(data[1][0])
        sku = True
    except ValueError:
        sku = False

    # Open a connection to the master database.
    connection = sqlite3.connect(isql.MASTER)

    # Get the product hash.
    match = isql.getProductHash(connection)

    # Convert the basis column from skus to product codes.
    if sku:
        for row in data:
            try:
                row[0] = match[row[0]]
            except KeyError:
                tempID = isql.addMissing(row[0], connection)
                row[0] = "TEMP-" + str(tempID)

    # Close the connection and commit changes to the master database.
    connection.commit()
    connection.close()

    return data

def decompose(source, dateFormat, shift=False):
    """
    The point of the decompose function is to take a file with an arbitrary
    header and extract only relevent information, based on associations with a
    database.
    """

    # Open the file and extract the header.
    with open(source, newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='|')
        header = next(reader)
        first = next(reader)

    # Get the variable hash table.
    varHash = isql.getVariableHash()

    # Iterate over the header matching its titles to known variables.
    match = []
    remove = []
    hasDate = False
    firstDate = True
    index = 0
    for col in header:
        col = col.lower()
        # If the column item is in the keys list, match the variable.
        try:
            variable = varHash[col]
            match.append(variable)

            # If the variable is Date get the first date from the data.
            if variable == "Date":
                firstDate = bool(checkDate(first[index], dateFormat))

            # If the variable is Ignore add the index to the remove list.
            if variable == "Ignore":
                remove.append(index)
        # If not, add the title to the Missing variable list and the index to
        # the remove list.
        except KeyError:
            date = checkDate(col, dateFormat)
            if not date:
                match.append("Missing")
                remove.append(index)
            else:
                if shift:
                    match.append(date + dt.timedelta(weeks=4))
                else:
                    match.append(date)
                hasDate = True

        # Increment the index.
        index += 1

    return header, match, hasDate, firstDate

def decomposeCut(source, dateFormat, shift=False):
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
    varHash = isql.getVariableHash()

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
            date = checkDate(col, dateFormat)
            if not date:
                match.append("Missing")

                # Add the missing variables to the missing list.
                isql.addAlias("Missing", col)

                # Add the missing variables to the remove list.
                remove.append(index)
            else:
                if shift:
                    match.append(date + dt.timedelta(weeks=4))
                else:
                    match.append(date)

        # Increment the index.
        index += 1

    # Recombine the matched header with data.
    data[0] = match.copy()

    # Remove any column that was labeled Ignore or Missing.
    remove = sorted(remove, reverse=True)
    for row in data:
        for i in remove:
            del row[i]

    # Convert empty strings to zeros.
    data = zeroOut(data)

    # Change an empty string to be none.
    if dateFormat == '':
        dateFormat = None

    # Date and time now.
    dateNow = dt.datetime(1, 1, 1).now()

    # Create the file info dictionary.
    fileInfo = {"location": source,
        "date_of_import": dateNow.strftime("%Y-%m-%d %H:%M:%S"),
        "date_format": dateFormat}

    # Add the import to the database.
    importID = isql.addImport(fileInfo)

    # Create the title of the decomposed file.
    output = ''.join([isql.DATA, "imported/", str(importID), '-',
        fileInfo["date_of_import"], ".csv"])

    # Open the file and write the data.
    with open(output, 'w', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=',', quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow(row)

    return data

def aggregate(data):
    """
    Data must:
      Be sorted by product
      Have product as the first column
      Not have a header
    """

    # Initialize the aggregated list.
    allData = []

    # Initialize single product list.
    prod = [int(x) for x in data[0][1:]]
    prod.insert(0, data[0][0])

    # Iterate over the rows in the data and aggregate if the same product.
    index = 1
    for row in data[1:]:
        name = row[0]
        if name == prod[0]:
            temp = [int(x) for x in data[index][1:]]
            prod = list(map(add, prod[1:], temp))
            prod.insert(0, name)
        else:
            allData.append(prod)
            prod = [int(x) for x in data[index][1:]]
            prod.insert(0, name)

        # Increment the index.
        index += 1

    # Append the final single product list to the aggregated list.
    allData.append(prod)

    return allData

def checkDate(posDate, dateFormat):
    """
    """

    # Check to make sure they are the same size.
    if len(posDate) != len(dateFormat):
        return False

    # Dict of the form {day: ?, week: ?, month: ?, year: ?}
    date = {'d': '', 'w': '', 'm': '', 'y': ''}

    try:
        index = 0
        for char in dateFormat:
            if char in date.keys():
                date[char] = date[char] + posDate[index]

            index += 1

        if len(date['y']) == 2:
            date['y'] = int(date['y']) + 2000

        if len(date['d']) > 0:
            convert = dt.date(int(date['y']), int(date['m']), int(date['d']))
        else:
            if len(date['w']) > 0:
                convert = isoToGregorian(int(date['y']), int(date['w']), 1)
            else:
                convert = dt.date(int(date['y']), int(date['m']), 1)
    except ValueError:
        return False

    return convert

def zeroOut(data):
    """
    """

    # Convert empty strings to zeros.
    cols = len(data[0])
    data = [0 if col == '' else col for row in data for col in row]
    data = [data[y : y + cols] for y in range(0, len(data), cols)]

    return data

def isoYearStart(isoYear):
    """
    The gregorian calendar date of the first day of the given ISO year.
    """

    fourthJan = dt.date(isoYear, 1, 4)
    delta = dt.timedelta(fourthJan.isoweekday() - 1)

    return fourthJan - delta 

def isoToGregorian(isoYear, isoWeek, isoDay):
    """
    Gregorian calendar date for the given ISO year, week and day.
    """

    yearStart = isoYearStart(isoYear)

    return yearStart + dt.timedelta(days=isoDay - 1, weeks=isoWeek - 1)
