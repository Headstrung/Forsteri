"""
File Module

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

# Import python modules.
import copy
import csv
import datetime as dt
import sqlite3

# Import forsteri modules.
from forsteri.interface import data as idata
from forsteri.interface import sql as isql

class Header(object):
    """
    """

    def __init__(self, location, date_template, shift):
        """
        """

        # Define the file absolute location.
        self.location = location

        # Define the date format.
        self.date_template = date_template

        # Define the shift flag.
        self.shift = shift

        # Read in the header.
        self.read_header()

        # Define the matched header.
        self.match()

        # Define the reduced matched header.
        self.reduce()

    def get_location(self):
        """
        """

        return self.location

    def set_location(self, location):
        """
        """

        # Update the location.
        self.location = location

        # Read the new header.
        self.read_header(location)

        # Match the new header.
        self.match()

    def get_basis_index(self):
        """
        """

        return self.matched_header.index("Basis")

    def get_date_index(self):
        """
        """

        return self.matched_header.index("Date")

    def read_header(self):
        """
        """

        # Read in the header values.
        with open(self.location) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            self.header = next(reader)

    def match(self):
        """
        """

        # Get the variable hash table.
        variable_hash = isql.getVariableHash()

        # Get the date templates.
        date_templates = [date[1:] for date in isql.getForVariable("Date") if\
            date[0] == '$']

        # Iterate over the header values and match them to know variables.
        self.matched_header = []
        for item in self.header:
            try:
                self.matched_header.append(variable_hash[item.lower()])
            except KeyError:
                try:
                    self.matched_header.append(self.check_date(item))
                except (AssertionError, ValueError, TypeError):
                    self.matched_header.append("Missing")

    def reduce(self):
        """
        """

        # Iterate over the matched header and remove columns.
        self.reduced_matched_header = [item for item in self.matched_header\
            if item not in ["Ignore", "Missing", "Basis"]]

    def check_date(self, possible_date):
        """
        """

        # Check if the lengths match first.
        assert len(possible_date) == len(self.date_template)

        # Iterate over the date and assign each character to the date id.
        components = {'y': [], 'm': [], 'w': [], 'd': []}
        for char, value in zip(self.date_template, possible_date):
            try:
                components[char].append(value)
            except KeyError:
                continue

        # Convert the year to an integer.
        year = int(''.join(components['y']))
        try:
            day = int(''.join(components['d']))
        except ValueError:
            day = 1

        # Check if a week was given, if so, convert, otherwise create date.
        if len(components['w']) > 0:
            date = self.iso_to_gregorian(year, int(''.join(components['w'])),
                day)
        else:
            date = dt.date(year, int(''.join(components['m'])), day)

        return date

    def iso_year_start(self, iso_year):
        """
        The gregorian calendar date of the first day of the given ISO year.
        """

        fourth_jan = dt.date(iso_year, 1, 4)
        delta = dt.timedelta(fourth_jan.isoweekday() - 1)

        return fourth_jan - delta

    def iso_to_gregorian(self, iso_year, iso_week, iso_day):
        """
        Gregorian calendar date for the given ISO year, week and day.
        """

        year_start = self.iso_year_start(iso_year)

        return year_start + dt.timedelta(days=iso_day - 1, weeks=iso_week - 1)

class File(object):
    """
    """

    def __init__(self, location, date_template, shift):
        """
        """

        # Define the file location.
        self.location = location

        # Define the date format.
        self.date_template = date_template

        # Define the shift flag.
        self.shift = shift

        # Read the data from the file.
        self.read_data()

        # Create the header.
        self.header = Header(location, date_template, shift)

        # Define the reduced data.
        self.reduce()

        # Convert the basis.
        self.convert_basis()

        # Convert the data.
        self.convert_data()

    def __getitem__(self, keys):
        """
        """

        # Check to make sure the correct values are input, if not set standard.
        try:
            identifier, kind = keys
        except TypeError:
            identifier = keys
            kind = "Basis"
        except ValueError:
            identifier = keys[0]
            kind = "Basis"

        # Collect the correct values based on the input.
        if kind == "Header":
            col_index = self.header.reduced_matched_header.index(identifier)
            values = [row[col_index] for row in self.reduced_data]
        elif kind == "Basis":
            row_index = self.basis.index(identifier)
            values = self.reduced_data[row_index]
        else:
            raise NameError("{} is not a valid kind.".format(kind))

        return values

    def get_location(self):
        """
        """

        return self.location

    def set_location(self, location):
        """
        """

        # Update the new location.
        self.location = location

        # Read the new data.
        self.read_data(location)

        # Set the new header location.
        self.header.set_location(location)

    def get_header(self):
        """
        """

        return self.header

    def set_header(self, header):
        """
        """

        # Make sure the input is the correct type.
        assert isinstance(header, Header)

        self.header = header

    def read_data(self):
        """
        """

        # Read in the header values.
        self.data = []
        with open(self.location) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in reader:
                self.data.append(row)

        # Delete the header row.
        del self.data[0]

    def reduce(self):
        """
        """

        # Get the indices of the columns that should be kept.
        keep = [index for index in range(0, len(self.header.matched_header))\
            if self.header.matched_header[index] not in ["Ignore", "Missing",
            "Basis"]]

        # Iterate over the data and only take the columns that are required,
        # while extracting basis values.
        self.reduced_data = []
        self.basis = []
        basis_index = self.header.get_basis_index()
        for row in self.data:
            self.reduced_data.append([row[take] for take in keep])
            self.basis.append(row[basis_index])

    def convert_basis(self):
        """
        """

        # Get the product hash table.
        product_hash = isql.getProductHash()

        # Iterate over the reduced data and convert the basis.
        self.missing_basis = []
        for index in range(0, len(self.basis)):
            try:
                self.basis[index] = product_hash[self.basis[index]]
            except KeyError:
                self.missing_basis.append(self.basis[index])

    def convert_data(self):
        """
        Convert the variables to numbers, missing values to zeros, and date
        column to datetime.
        """

        # Convert numbers to floats and empty strings to zeros.
        col_count = len(self.reduced_data[0])
        temp = [0 if col == '' else float(col) for row in self.reduced_data \
            for col in row]
        self.reduced_data = [temp[y : y + col_count] for y in range(0,
            len(temp), col_count)]

        # 
        #try:
        #    date_index = self.header.get_date_index()
        #    for row in self.reduced_data:
        #        row[date_index] = self.header.check_date(row[date_index])
        #except ValueError:
        #    pass

    def aggregate(self):
        """
        """

        pass

if __name__ == "__main__":
    pass
