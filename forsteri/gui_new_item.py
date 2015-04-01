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
        contentSizer = wx.FlexGridSizer(6, 2, 5, 10)

        # Create a list of input texts.
        texts = ["Name", "Class", "Category", "Subcategory", "Account"]

        # Get the list of choices for each text.
        choices = self.pullChoices(texts)

        # Create the input text and controls.
        self.inputs = dict()
        for text in texts:
            if text == "Name":
                self.inputs[text] = wx.TextCtrl(masterPanel, size=(150, -1))
            else:
                self.inputs[text] = wx.ComboBox(masterPanel, size=(150, -1),
                    choices=choices[text], style=wx.CB_READONLY|wx.CB_SORT)

            # Add everything to the content sizer.
            contentSizer.AddMany([wx.StaticText(masterPanel, label=text),
                self.inputs[text]])

        # Create the forecast button.
        forecastButton = wx.Button(masterPanel, label="Forecast")

        # Bind the forecast button press to a function.
        forecastButton.Bind(wx.EVT_BUTTON, self.onForecast)

        ## Related Products
        # Create the header static box.
        relatedSB = wx.StaticBox(masterPanel, label="Related Products")

        # Create the header sizer.
        relatedSizer = wx.StaticBoxSizer(relatedSB, wx.VERTICAL)

        # Create the list control.
        self.relatedList = wx.ListCtrl(masterPanel, size=(300, 200),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.relatedList.InsertColumn(0, "Product", width=140)
        self.relatedList.InsertColumn(1, "Release Value", width=140)

        # Add the header list to the header sizer.
        relatedSizer.Add(self.relatedList, flag=wx.ALL, border=5)

        ## Frame Operations
        # Add everything to the master sizer.
        masterSizer.Add(contentSizer, flag=wx.TOP|wx.ALIGN_CENTER, border=10)
        masterSizer.Add(forecastButton, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        masterSizer.Add(relatedSizer, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|
            wx.ALIGN_CENTER, border=5)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((300, 400))
        self.SetTitle("New Item Forecast")
        self.Centre()
        self.Show(True)

    def pullChoices(self, tiers):
        """
        """

        # Get the choices for each tier.
        choices = dict()
        for tier in tiers:
            if tier == "Name":
                pass
            else:
                choice = ['']
                choice.extend(isql.getForTier(tier))
                choices[tier] = choice

        return choices

    def onForecast(self, event):
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
        del description["Name"]
        products = [x[0] for x in isql.getData(description)]

        # Remove all items from the list control and reset the index.
        self.relatedList.DeleteAllItems()

        # 
        index = 0
        for product in products:
            self.relatedList.InsertItem(index, product)
            try:
                self.relatedList.SetItem(index, 1, str(idata.getData(product,
                    "finished_goods", connection=connection)[0][1]))
            except IndexError:
                self.relatedList.SetItem(index, 1, "0")

            index += 1

"""
Start Application
"""
def main():
    """
    When the file is called independently create and display the manager frame.
    """

    app = wx.App()
    NewItemFrame(None, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
