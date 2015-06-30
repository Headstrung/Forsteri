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
import operator as op
import sqlite3

# Import forsteri modules.
from forsteri.interface import data as idata
from forsteri.interface import sql as isql

class File(object):
    """
    """

    def __init__(self, location, date_template, shift, date=None,
        variable=None):
        """
        """

        # Define the file location.
        self.location = location

        # Define the date format.
        self.date_template = date_template

        # Define the shift flag.
        self.shift = shift

        # Define the date.
        if date is None:
            self.date = None
        else:
            self.date = self.check_date(date)

        # Define the variable.
        self.variable = variable

        # Read the data from the file.
        self.data = []
        with open(self.location) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in reader:
                self.data.append(row)

        # If there is no data there is nothing to do.
        if len(self.data) < 2:
            raise AssertionError("No data to load.")
            return

        # Match the header values to known variables.
        self.match()

        # Make sure a basis column has been found.
        if "Basis" not in self.matched_header:
            raise AssertionError("A basis column must be defined.")

        # Define the kind of file it is. 0 - Multidimentional Timeseries,
        # 1 - Single-dimensional Timeseries, 2 - Cross Sectional Data.
        if "Date" in self.matched_header:
            self.kind = 0
        else:
            ts = False
            for value in self.matched_header:
                if isinstance(value, dt.date):
                    ts = True
                    break
            if ts:
                self.kind = 1
                if self.variable is None:
                    raise AssertionError("A variable must be input for this \
kind of file.")
            else:
                self.kind = 2
                if self.date is None:
                    raise AssertionError("A date must be input for this kind \
of file.")
                    return

        # Define the reduced data.
        self.reduce()

        # If there are no columns remaining there is no data.
        if len(self.reduced_matched_header) == 0:
            raise AssertionError("No data to load.")
            return

        # Extract the header.
        self.header = self.data[0]

        # Delete the header row from the data.
        del self.data[0]

        # Convert the dates.
        self.convert_dates()

        # Convert the basis.
        self.convert_basis()

        # Convert the data.
        self.convert_data()

        # Aggregate repeats.
        self.aggregate()

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
            col_index = self.reduced_matched_header.index(identifier)
            values = [row[col_index] for row in self.reduced_data]
        elif kind == "Basis":
            row_index = self.basis.index(identifier)
            values = self.reduced_data[row_index]
        else:
            raise NameError("{} is not a valid kind.".format(kind))

        return values

    def __getitem__(self, inputs):
        """
        """

        basis_index = self.agg_basis.index(inputs[0])
        variable_index = self.reduced_matched_header.index(inputs[1])

        return self.reduced_data[basis_index][variable_index]

    def get_location(self):
        """
        """

        return self.location

    def set_location(self, location):
        """
        """

        self.__init__(location, self.date_template, self.shift)

    def get_header(self):
        """
        """

        return self.header

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
        for item in self.data[0]:
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

        # Get the indices of the columns that should be kept.
        keep = [index for index in range(0, len(self.matched_header))\
            if self.matched_header[index] not in ["Ignore", "Missing",
            "Basis"]]

        # Iterate over the data and only take the columns that are required,
        # while extracting basis values.
        self.reduced_matched_header = [self.matched_header[take] for\
            take in keep]
        self.reduced_data = []
        self.basis = []
        basis_index = self.matched_header.index("Basis")
        for row in self.data[1:]:
            self.reduced_data.append([row[take] for take in keep])
            self.basis.append(row[basis_index])

        # Sort the data by the basis.
        if self.kind == 0:
            temp = sorted(zip(self.basis, self.reduced_data),
                key=lambda pair: (pair[0],
                pair[1][self.reduced_matched_header.index("Date")]))
        else:
            temp = sorted(zip(self.basis, self.reduced_data),
                key=lambda pair: pair[0])
        for i, (j, k) in enumerate(temp):
            self.basis[i] = j
            self.reduced_data[i] = k

    def convert_dates(self):
        """
        """

        # Convert dates in date column to datetime objects.
        self.dates = []
        try:
            reduced_date_index = self.reduced_matched_header.index("Date")
            for row in self.reduced_data:
                self.dates.append(self.check_date(row[reduced_date_index]))
                del row[reduced_date_index]
            del self.reduced_matched_header[reduced_date_index]
        except ValueError:
            pass

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

    def aggregate(self):
        """
        """

        # Aggregate by sum.
        if self.kind == 0:
            index = 0
            self.agg_basis = []
            self.agg_dates = []
            self.agg_reduced_data = []
            for base in self.unique(self.basis):
                repeats = self.find_all(self.basis, base)
                self.agg_basis.append(base)
                self.agg_dates.append(self.dates[repeats[0]])
                self.agg_reduced_data.append(self.reduced_data[repeats[0]])
                for i in repeats[1:]:
                    if self.dates[i - 1] == self.dates[i]:
                        self.agg_reduced_data[index] = \
                            self.add_array(self.agg_reduced_data[index],
                            self.reduced_data[i])
                    else:
                        index += 1
                        self.agg_basis.append(base)
                        self.agg_dates.append(self.dates[i])
                        self.agg_reduced_data.append(self.reduced_data[i])
                index += 1
        else:
            index = 0
            self.agg_basis = [self.basis[0]]
            self.agg_reduced_data = [self.reduced_data[0]]
            for i in range(1, len(self.basis)):
                if self.basis[i - 1] == self.basis[i]:
                    self.agg_reduced_data[index] = \
                        self.add_array(self.agg_reduced_data[index],
                        self.reduced_data[i])
                else:
                    index += 1
                    self.agg_basis.append(self.basis[i])
                    self.agg_reduced_data.append(self.reduced_data[i])

    def check_date(self, possible_date):
        """
        """

        # Check if the lengths match first.
        if len(possible_date) != len(self.date_template):
            raise AssertionError("The date template does not apply to all \
found dates.")

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

        # Check if the shift flag is true.
        if self.shift:
            date = date + dt.timedelta(weeks=4)

        return date

    def write(self, overwrite, variable=None):
        """
        """

        # Open a connection to the data database.
        connection = sqlite3.connect(idata.MASTER)

        # Write the file data to the database.
        if self.kind == 0:
            for (i, entry) in enumerate(self.agg_reduced_data):
                product = self.agg_basis[i]
                date = self.agg_dates[i]
                for (j, value) in enumerate(entry):
                    idata.addData(idata.toSQLName(\
                        self.reduced_matched_header[j]),
                        (date, product, value), overwrite, connection)
        elif self.kind == 1:
            for (i, row) in enumerate(self.agg_reduced_data):
                product = self.agg_basis[i]
                for (j, col) in enumerate(row):
                    idata.addData(idata.toSQLName(self.variable),
                        (self.reduced_matched_header[j], product, col),
                        overwrite, connection)
        else:
            for (i, row) in enumerate(self.agg_reduced_data):
                product = self.agg_basis[i]
                for (j, col) in enumerate(row):
                    idata.addData(idata.toSQLName(\
                        self.reduced_matched_header[j]), (self.date, product,
                        col), overwrite, connection)

        # Commit changes and close database.
        connection.commit()
        connection.close()

        pass

    def add_array(self, X, Y):
        """
        """

        if len(X) != len(Y):
            raise AssertionError("Arrays must be the same length to add.")

        return [X[i] + Y[i] for i in range(0, len(X))]

    def find_all(self, seq, item):
        """
        """

        repeats = []

        for (index, value) in enumerate(seq):
            if value == item:
                repeats.append(index)

        return repeats

    def unique(self, seq):
        """
        seq must be sorted.
        """

        previous = ''

        for value in seq:
            if value != previous:
                previous = value
                yield value
            else:
                continue

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

if __name__ == "__main__":
    pass
