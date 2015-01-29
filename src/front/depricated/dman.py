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
        labelStrings = ["Account:", "Class:", "Category:", "Subcategory:",
            "Product:"]
        choices = self.getChoices()

        # Create the labels and input boxes.
        labels = [None] * 5
        inputs = [None] * 5
        for i in range(0, 5):
            labels[i] = wx.StaticText(masterPanel, label=labelStrings[i])
            if i < 4:
                inputs[i] = wx.ComboBox(masterPanel, choices=choices[i])
            else:
                inputs[i] = wx.TextCtrl(masterPanel, size=(150, -1))

        # Add the label and combo boxes to the search sizer.
        searchSizer.AddMany(labels)
        searchSizer.AddMany(inputs)

        """Initialize the list control."""
        self.productList = wx.ListCtrl(masterPanel, size=(-1, 200),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.productList.InsertColumn(0, "Product")
        self.productList.InsertColumn(1, "Account")
        self.productList.InsertColumn(2, "Class")
        self.productList.InsertColumn(3, "Category")
        self.productList.InsertColumn(4, "Subcategory", width=100)
        self.updateList()

        """Initialize the manipulate buttons."""
        # Create the manipulate sizer.
        manipSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        newButton = wx.Button(masterPanel, label="&New")
        editButton = wx.Button(masterPanel, label="&Edit")
        deleteButton = wx.Button(masterPanel, label="&Delete")

        # Add the buttons to the manipulate sizer.
        manipSizer.AddMany([newButton, editButton, deleteButton])

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

        # Add the buttons to the finish sizer.
        finishSizer.Add(okButton)
        finishSizer.Add(cancelButton)

        # Bind the button presses to function.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        """Final frame operations."""
        # Add everything to the master sizer.
        masterSizer.Add(searchSizer, 0, wx.ALIGN_CENTER)
        masterSizer.Add(self.productList, 0, wx.ALL|wx.EXPAND, 5)
        masterSizer.Add(manipSizer, 0, wx.ALIGN_CENTER)
        masterSizer.Add(finishSizer, 0)

        # Set the sizer for the main panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetMinSize((600, 350))
        self.SetSize((600, 350))
        self.SetTitle("Data Manager")
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
            connect.append(iface.getTierList(tier))

        return connect

    def updateList(self):
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

        print("Finished")

    def onCancel(self, event):
        """
        """

        self.Close()

""" Start Application """
def main():
    """
    """

    app = wx.App()
    ManagerFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
