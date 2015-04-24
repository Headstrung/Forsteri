#!/usr/bin/python

"""
New Item Forecasting Frame

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
import sqlite3
import wx

"""
Constant Declarations
"""


"""
Frame Class
"""
class NewItemFrame(wx.Frame):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        ## Frame
        # Initialize by the parent's constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## Input Section
        # Create the input sizer.
        contentSizer = wx.FlexGridSizer(4, 2, 5, 10)

        # Create a list of input texts.
        texts = ["Class", "Category", "Subcategory", "Retailer Type"]

        # Get the list of choices for each text.
        choices = self.pullChoices(texts)

        # Create the input text and controls.
        self.inputs = {}
        for text in texts:
            self.inputs[text] = wx.ComboBox(masterPanel, size=(150, -1),
                choices=choices[text], style=wx.CB_READONLY|wx.CB_SORT)

            # Add everything to the content sizer.
            contentSizer.AddMany([wx.StaticText(masterPanel, label=text),
                self.inputs[text]])

        # Create the forecast button.
        generateButton = wx.Button(masterPanel, label="Generate")

        # Bind the forecast button press to a function.
        generateButton.Bind(wx.EVT_BUTTON, self.onGenerate)

        ## Related Products
        # Create the related static box.
        relatedSB = wx.StaticBox(masterPanel, label="Related Products")

        # Create the related sizer.
        relatedSizer = wx.StaticBoxSizer(relatedSB, wx.VERTICAL)

        # Create the list control.
        self.relatedList = wx.ListCtrl(masterPanel, size=(300, 200),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.relatedList.InsertColumn(0, "Product", width=140)
        self.relatedList.InsertColumn(1, "Release Value", width=140)

        # Add the related list to the related sizer.
        relatedSizer.Add(self.relatedList, flag=wx.ALL, border=5)

        ## Information
        # Create the info static box.
        infoSB = wx.StaticBox(masterPanel, label="Summary")

        # Create the info sizer.
        infoSizer = wx.StaticBoxSizer(infoSB, wx.VERTICAL)

        # Create the info grid sizer.
        infoGridSizer = wx.FlexGridSizer(7, 2, 0, 0)

        # Create the info items.
        labelItems = [wx.StaticText(masterPanel, label="Maximum:"),
            wx.StaticText(masterPanel, label="3rd Quartile:"),
            wx.StaticText(masterPanel, label="Average:"),
            wx.StaticText(masterPanel, label="Median:"),
            wx.StaticText(masterPanel, label="1st Quartile:"),
            wx.StaticText(masterPanel, label="Minimum:")]

        self.infoItems = [wx.StaticText(masterPanel, label=''),
            wx.StaticText(masterPanel, label=''),
            wx.StaticText(masterPanel, label=''),
            wx.StaticText(masterPanel, label=''),
            wx.StaticText(masterPanel, label=''),
            wx.StaticText(masterPanel, label='')]

        # Add the items to the left sizer.
        for i in range(0, 6):
            infoGridSizer.Add(labelItems[i], flag=wx.LEFT|wx.TOP, border=5)
            infoGridSizer.Add(self.infoItems[i], flag=wx.LEFT|wx.TOP, border=5)
        infoGridSizer.AddSpacer(5)

        # 
        #infoGridSizer.AddGrowableCol(0)

        # Add the  sizer to the info sizer.
        infoSizer.Add(infoGridSizer, flag=wx.EXPAND)

        ## Frame Operations
        # Add everything to the master sizer.
        masterSizer.Add(contentSizer, flag=wx.TOP|wx.ALIGN_CENTER, border=10)
        masterSizer.Add(generateButton, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        masterSizer.Add(relatedSizer, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|
            wx.ALIGN_CENTER, border=5)
        masterSizer.Add(infoSizer, flag=wx.ALL|wx.ALIGN_CENTER|wx.EXPAND,
            border=5)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((328, 577))
        self.SetTitle("New Item Forecast")
        self.Centre()
        self.Show(True)

    """
    Helper Functions
    """
    def pullChoices(self, tiers):
        """
        """

        # Get the choices for each tier.
        choices = dict()
        for tier in tiers:
            choice = ['']
            choice.extend(isql.getForTier(tier))
            choices[tier] = choice

        return choices

    def summary(self, data):
        """
        """

        # Copy, find the length, and sort the data.
        dataCopy = data.copy()
        dataLen = len(dataCopy)
        dataCopy.sort()

        # Find the maximum and mean of the data.
        summary = [dataCopy[-1]]
        summary.append(sum(dataCopy) / dataLen)

        # Iterate over each quartile.
        for i in range(3, 0, -1):
            q = i * (dataLen - 1)
            summary.append(self.quartile(dataCopy, q // 4, q % 4))

        # Find the minimum.
        summary.append(dataCopy[0])

        # Swap the mean.
        summary[1], summary[2] = summary[2], summary[1]

        return summary

    def quartile(self, data, i, r):
        """
        """

        return data[i] + (r / 4) * (data[i + 1] - data[i])

    """
    Event Handlers
    """
    def onGenerate(self, event):
        """
        """

        # Open a connection to the data database.
        connection = sqlite3.connect(idata.MASTER)

        # Get the selections.
        selections = {key: value.GetValue() for (key, value) in\
            self.inputs.items()}

        # Check if there are no inputs.
        if sum([1 if x == '' else 0 for x in selections.values()]) ==\
            len(selections):
            return

        # Get the data from the selections.
        description = selections.copy()
        products = [x[0] for x in isql.getData(description)]

        # Remove all items from the list control and reset the index.
        self.relatedList.DeleteAllItems()

        # 
        index = 0
        first = []
        for product in products:
            try:
                first.append(idata.getData(product, "finished_goods_monthly",
                    connection=connection)[0][1])

                self.relatedList.InsertItem(index, product)
                self.relatedList.SetItem(index, 1, str(int(first[index])))

                index += 1
            except IndexError:
                continue

        # Get the summary statistics.
        try:
            summary = self.summary(first)
        except IndexError:
            return

        # Set each value.
        i = 0
        for item in self.infoItems:
            item.SetLabel(str(round(summary[i])))
            i += 1

"""
Start Application
"""
def main():
    """
    When the file is called independently create and display the manager frame.
    """

    app = wx.App()
    NewItemFrame(None, style=wx.DEFAULT_FRAME_STYLE)#^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
