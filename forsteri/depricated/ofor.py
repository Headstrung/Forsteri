#!/usr/bin/python

"""
Open Forecast Frame

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
import interface as iface
import wx

""" Frame Class """
class ManagerFrame(wx.Frame):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        super(ManagerFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        """
        """

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        """Initialize the search by combo boxes."""
        # Create the search sizer.
        searchSizer = wx.FlexGridSizer(2, 5, 5, 5)

        # Get the label strings and combo box choices.
        labelStrings = ["Product:", "Account:", "Class:", "Category:",
            "Subcategory:"]
        choices = self.getChoices()

        # Create the labels and input boxes.
        labels = [None] * 5
        self.inputs = [None] * 5
        for i in range(0, 5):
            labels[i] = wx.StaticText(masterPanel, label=labelStrings[i])
            if i == 0:
                self.inputs[i] = wx.TextCtrl(masterPanel, size=(150, -1))
            else:
                self.inputs[i] = wx.ComboBox(masterPanel,
                    choices=choices[i - 1], style=wx.CB_READONLY|wx.CB_SORT)

        # Add the label and combo boxes to the search sizer.
        searchSizer.AddMany(labels)
        searchSizer.AddMany(self.inputs)

        """Initialize the list control."""
        self.productList = wx.ListCtrl(masterPanel, size=(-1, 400),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)
        self.productList.InsertColumn(0, "Product", width=136)
        self.productList.InsertColumn(1, "Account", width=136)
        self.productList.InsertColumn(2, "Class", width=136)
        self.productList.InsertColumn(3, "Category", width=136)
        self.productList.InsertColumn(4, "Subcategory", width=136)
        self.updateList(None)

        """Initialize the manipulate buttons."""
        # Create the manipulate sizer.
        manipSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        newButton = wx.Button(masterPanel, label="&New")
        editButton = wx.Button(masterPanel, label="&Edit")
        deleteButton = wx.Button(masterPanel, label="&Delete")

        # Add the buttons to the manipulate sizer.
        manipSizer.AddMany([newButton, (5, 0), editButton, (5, 0),
            deleteButton])

        # Bind button presses to functions.
        newButton.Bind(wx.EVT_BUTTON, self.onNew)
        editButton.Bind(wx.EVT_BUTTON, self.onEdit)
        deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

        """Initialize the finish buttons."""
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        okButton = wx.Button(masterPanel, label="&OK")
        cancelButton = wx.Button(masterPanel, label="&Cancel")

        # Set the OK button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([okButton, (5, 0), cancelButton, (5, 0)])

        # Bind the button presses to function.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        """Final frame operations."""
        # Add everything to the master sizer.
        masterSizer.AddSpacer(10)
        masterSizer.Add(searchSizer, flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(10)
        masterSizer.Add(self.productList, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=5)
        masterSizer.AddSpacer(10)
        masterSizer.Add(manipSizer, flag=wx.ALIGN_CENTER)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(680, 20)),
            flag=wx.ALIGN_CENTER)
        masterSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT)
        masterSizer.AddSpacer(5)

        # Set the sizer for the main panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((700, 595))
        self.SetTitle("Open Forecast")
        self.Centre()
        self.Show(True)

    def getChoices(self):
        """
        """

        # Get the list of tiers.
        tiers = iface.getTiers()

        # Get each list associated with each tier.
        connect = []
        for tier in tiers:
            tierList = iface.getTierList(tier)

            # Add an empty string for selection.
            tierList.append("")

            # Append the entire list to the returned list.
            connect.append(tierList)

        return connect

    def updateList(self, event):
        """
        """

        pass

    def onNew(self, event):
        """
        """

        pass

    def onEdit(self, event):
        """
        """

        pass

    def onDelete(self, event):
        """
        """

        pass

    def onOK(self, event):
        """
        """

        self.Close()

    def onCancel(self, event):
        """
        """

        self.Close()

""" Start Application """
def main():
    """
    """

    app = wx.App()
    ManagerFrame(None)#, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
