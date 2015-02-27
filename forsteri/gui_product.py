#!/usr/bin/python

"""
Product Panel

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
import int_data as idata
import int_sql as isql
import wx

"""
Constant Declarations
"""


"""
Product Panel
"""
class ProductPanel(wx.Panel):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        ## Panel
        # Initialize the parents constructor.
        super().__init__(*args, **kwargs)

        # Create the master sizer.
        masterSizer = wx.GridBagSizer(5, 5)

        # Create the subsizers.
        #subSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        ## Product Information
        # Create the product information sizer.
        infoSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the static text for each attribute.
        self.nameText = wx.StaticText(self, label="Product")
        self.accountText = wx.StaticText(self, label="Account")
        self.classText = wx.StaticText(self, label="Class")
        self.categoryText = wx.StaticText(self, label="Category")
        self.subcategoryText = wx.StaticText(self, label="Subcategory")

        # Create the fonts for the static texts.
        titleFont = wx.Font(22, wx.SWISS, wx.NORMAL, wx.BOLD)
        infoFont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.LIGHT)

        # Set the fonts for the static texts.
        self.nameText.SetFont(titleFont)
        self.accountText.SetFont(infoFont)
        self.classText.SetFont(infoFont)
        self.categoryText.SetFont(infoFont)
        self.subcategoryText.SetFont(infoFont)

        # Add the static text to the sizer.
        infoSizer.Add(self.nameText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.accountText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.classText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.categoryText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.subcategoryText, flag=wx.LEFT, border=5)

        ## Variables
        # Create the variables static box.
        variablesSB = wx.StaticBox(self, label="Variables")

        # Create the variables sizer.
        variablesSizer = wx.StaticBoxSizer(variablesSB, wx.VERTICAL)

        # Create the list control.
        self.variablesList = wx.ListCtrl(self, size=(250, 100),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.variablesList.InsertColumn(0, "Variable", width=150)
        self.variablesList.InsertColumn(1, "Latest Data", width=100)

        # Add the list control to the sizer.
        variablesSizer.Add(self.variablesList, flag=wx.ALL, border=5)

        ## Related Items
        # Create the related items static box.
        relatedSB = wx.StaticBox(self, label="Related Items")

        # Create the related items sizer.
        relatedSizer = wx.StaticBoxSizer(relatedSB, wx.VERTICAL)

        # Create the list box.
        self.relatedList = wx.ListBox(self, size=(150, 100))

        # Add the list box to the sizer.
        relatedSizer.Add(self.relatedList, flag=wx.ALL, border=5)

        ## Linked Items
        # Create the related items static box.
        linkedSB = wx.StaticBox(self, label="Linked Items")

        # Create the related items sizer.
        linkedSizer = wx.StaticBoxSizer(linkedSB, wx.VERTICAL)

        # Create the list box.
        self.linkedList = wx.ListBox(self, size=(150, 100))

        # Add the list box to the sizer.
        linkedSizer.Add(self.linkedList, flag=wx.ALL, border=5)

        ## Panel Operations
        # Add everything to the master sizer.
        masterSizer.Add(infoSizer, pos=(0, 0), flag=wx.LEFT|wx.TOP, border=5)
        masterSizer.Add(variablesSizer, pos=(0, 1), flag=wx.TOP, border=5)
        masterSizer.Add(relatedSizer, pos=(0, 2), flag=wx.TOP, border=5)
        masterSizer.Add(linkedSizer, pos=(0, 3), flag=wx.TOP|wx.RIGHT,
            border=5)
        masterSizer.Add(wx.StaticLine(self), pos=(1, 0), span=(1, 4),
            flag=wx.EXPAND)

        # Make the first column growable.
        masterSizer.AddGrowableCol(0)

        # Set the master sizer for the panel.
        self.SetSizer(masterSizer)

    def setProduct(self, product):
        """
        """

        # Get the data for the product from the database.
        data = isql.getProduct(product)

        # Set the labels for the static texts.
        self.nameText.SetLabel(data[0])
        self.accountText.SetLabel(data[2])
        self.classText.SetLabel(data[3])
        self.categoryText.SetLabel(data[4])
        self.subcategoryText.SetLabel(data[5])

        # Get the variables.
        variables = idata.hasVariables(data[0], convert=True)

        # Get the latest data dates.
        latest = idata.latestData(data[0], variables, convert=True)

        # Remove all items from the variables list.
        self.variablesList.DeleteAllItems()

        # Add the new items to the variables list.
        index = 0
        for variable in variables:
            self.variablesList.InsertItem(index, variable)
            self.variablesList.SetItem(index, 1, latest[index])
            index += 1

        # Get the related products.
        related = isql.getData({"class": data[3], "category": data[4],
            "subcategory": data[5]})

        # Extract only the names of the related products.
        related = [x[0] for x in related]

        # Remove itself from the related list.
        related.remove(data[0])

        # Set the items for the related list.
        self.relatedList.SetItems(related)

        # Relayout the panel.
        self.Layout()

    def getProduct(self, product):
        """
        """

        pass
