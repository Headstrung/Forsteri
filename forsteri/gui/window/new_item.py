#!/usr/bin/python

"""
New Item Forecasting Frame

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

"""
Import Declarations
"""
import copy
import sqlite3
import wx

from forsteri.interface import data as idata
from forsteri.interface import sql as isql

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
        super(NewItemFrame, self).__init__(*args, **kwargs)

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
        self.relatedList.InsertColumn(1, "Release Value", width=130)

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
        self.SetSize((328, 616))
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
        dataCopy = copy.copy(data)
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

                self.relatedList.InsertStringItem(index, product)
                self.relatedList.SetStringItem(index, 1,
                    str(int(first[index])))

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
