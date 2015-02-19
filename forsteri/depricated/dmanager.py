#!/usr/bin/python

"""
Data Manager Frame

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

import csv
import h5py
import subprocess
import sys
import webbrowser
import wx
import wx.adv
import wx.grid
import wx.html
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)

class ManagerFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(ManagerFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create the master panel.
        self.masterPanel = wx.Panel(self)

        # Create the master sizer.
        self.masterSizer = wx.GridBagSizer(5, 5)

        # Create the static box and its sizer.
        staticBox = wx.StaticBox(self.masterPanel, label="Available products")
        gridSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)

        # Define combo box choices (until I get from db).
        labels = ["Accounts:", "Class:", "Category:", "Subcategory:",
            "Product:"]
        choices = [["CVS", "Walmart", "Walgreens", "Rite Aid"], ["Suncare",
            "Wound", "This", "That"], ["Foo", "Bar", "Baz"], ["Some", "Thing",
            "Else"]]

        searchSizer = wx.GridSizer(2, 5, 5, 5)

        # Create the combo boxes and product input field.
        textsSearch = []
        boxesSearch = []
        for i in range(0, 5):
            textsSearch.append(wx.StaticText(self.masterPanel,
                label=labels[i], style=wx.EXPAND | wx.ALIGN_CENTER))
            if i < 4:
                boxesSearch.append(wx.ComboBox(self.masterPanel,
                    choices=choices[i], style=wx.CB_READONLY | wx.ALL | wx.EXPAND | wx.ALIGN_CENTER))
            else:
                boxesSearch.append(wx.TextCtrl(self.masterPanel))

        for j in range(0, 5):
            searchSizer.Add(textsSearch[j])

        for k in range(0, 5):
            searchSizer.Add(boxesSearch[k])

        gridSizer.Add(searchSizer, flag=wx.EXPAND | wx.ALIGN_CENTER,
            border=10)

        # Set the grid flag.
        gridFlag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER

        # Create the grid.
        self.grid = wx.grid.Grid(self.masterPanel)

        # Add the grid to the grid sizer.
        gridSizer.Add(self.grid, flag=gridFlag, border=5)

        # Add the box sizer to the master sizer.
        self.masterSizer.Add(gridSizer, pos=(0, 0), span=(1, 5), flag=gridFlag,
            border=10)

        # Get the data to populate the grid with.

        # Set the dimentions of the grid.
        self.grid.CreateGrid(10, 5)

        #self.grid.SetCellValue(0, 3, "Hell yeah!")
        #self.grid.SetReadOnly(0, 3)

        """Initialize the combo boxes."""



        """Initialize the selection grid."""
        testList = [("CVS-B3RH1-00", "CVS", "Suncare", "Waist", "Shit"), ("EQT-SHITE-00", "Walmart", "This", "That", "The other thing"), ("q", "w", "e", "r", "t"), ("a", "s", "d", "f", "g")]
        self.listed = AutoWidthListCtrl(self.masterPanel)
        self.listed.InsertColumn(0, "Product", width=110)
        self.listed.InsertColumn(1, "Account", width=110)
        self.listed.InsertColumn(2, "Class", width=110)
        self.listed.InsertColumn(3, "Category", width=110)
        self.listed.InsertColumn(4, "Subcategory", width=110)

        for i in testList:
            index = self.listed.InsertItem(5, i[0])
            self.listed.SetItem(index, 1, i[1])
            self.listed.SetItem(index, 2, i[2])
            self.listed.SetItem(index, 3, i[3])
            self.listed.SetItem(index, 4, i[4])

        gridSizer.Add(self.listed, flag=wx.EXPAND, border=5)

        # Set the sizes and titles of individual rows and columns.
        #self.grid.SetRowSize(0, 60)
        #self.grid.SetColSize(0, 120)
        self.grid.SetRowLabelSize(0)
        self.grid.SetColLabelValue(0, "Product")
        self.grid.SetColLabelValue(1, "Account")
        self.grid.SetColLabelValue(2, "Class")
        self.grid.SetColLabelValue(3, "Category")
        self.grid.SetColLabelValue(4, "Subcategory")


        """Initialize the manipulate buttons."""
        newButton = wx.Button()


        """Initialize the exit buttons."""


        """ """
        self.masterSizer.AddGrowableCol(0)

        # Set the sizer for the main panel.
        self.masterPanel.SetSizer(self.masterSizer)

        # Set window properties.
        self.SetSize((600, 425))
        self.SetTitle("Data Manager")
        self.Centre()
        self.Show(True)

    def getData(self):
        # Open the database file.
        fid = h5py.File("../../data/database.h5", "r")

        # Initialize the returned data.
        products = []
        skus = []
        accounts = []
        classes = []
        categories = []
        scategories = []

        # Pull all the neccessary data from the database.
        for i in fid:
            products.append(i)
            skus.append(fid[i].attrs["sku"])
            if fid[i].attrs.__contains__("account"):
                accounts.append(fid[i].attrs["account"])
            if fid[i].attrs.__contains__("class"):
                classes.append(fid[i].attrs["class"])
            if fid[i].attrs.__contains__("account"):
                categories.append(fid[i].attrs["category"])
            if fid[i].attrs.__contains__("subcategory"):
                scategories.append(fid[i].attrs["subcategory"])

        # Close the database file.
        fid.close()

        return products, skus, accounts, classes, categories, scategories

    def onOpen(self, event):
        print("Opening")

    def onCancel(self, event):
        self.Close()

def main():
    app = wx.App()
    ManagerFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
