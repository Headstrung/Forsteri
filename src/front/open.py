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

import csv
import h5py
import subprocess
import webbrowser
import wx
import wx.html
import wx.adv

class OpenFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(OpenFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create the master panel.
        self.masterPanel = wx.Panel(self)

        # Create the master sizer.
        self.masterSizer = wx.GridBagSizer(5, 5)

        # Set the initial variables.
        self.currentSelect = "Account"

        """Initialize the radio buttons."""
        # Set comonly used variables.
        self.tiers = {"Account" : ["Account", "Product"], "Class" : ["Class",
            "Category", "Subcategory", "Product"]}
        buttonLabels = ["Account", "Class", "Component", "Chemical"]
        labelLen = len(buttonLabels)

        # Create the static box and its sizer.
        staticBox = wx.StaticBox(self.masterPanel, label="Search by")
        rbSizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)

        # Set the radio button flag.
        rbFlag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER

        # Create the initial radio button.
        radioButtons = [wx.RadioButton(self.masterPanel, label=buttonLabels[0],
            style=wx.RB_GROUP)]

        for i in range(0, labelLen):
            # Create the subsequent radio buttons.
            if i != 0:
                radioButtons.append(wx.RadioButton(self.masterPanel,
                    label=buttonLabels[i]))

            # Add the radio buttons to the box sizer.
            rbSizer.Add(radioButtons[i], flag=rbFlag, border=10)

            # Bind the selection of the radio buttons to an action.
            self.Bind(wx.EVT_RADIOBUTTON, lambda event, select=buttonLabels[i]:
                self.setSearch(event, select), radioButtons[i])

        # Add the box sizer to the master sizer.
        self.masterSizer.Add(rbSizer, pos=(0, 0), span=(1, 5), flag=rbFlag,
            border=10)

        """Initialize the combo boxes."""
        # Get the choice list.
        accounts = self.getComboList(self.currentSelect)

        # Set the combo box flag.
        cbFlag = wx.ALL | wx.EXPAND

        # Create the initial text and combo box.
        self.texts = [wx.StaticText(self.masterPanel,
            label=self.currentSelect)]
        self.boxes = [wx.ComboBox(self.masterPanel, choices=accounts,
            style=wx.CB_READONLY)]

        for i in range(0, 4):
            # Create the subsequent text and combo boxes and do not show them.
            if i != 0:
                self.texts.append(wx.StaticText(self.masterPanel,
                    label="Null"))
                self.boxes.append(wx.ComboBox(self.masterPanel, choices=[],
                    style=wx.CB_READONLY))
                self.texts[i].Show(False)
                self.boxes[i].Show(False)

            # Add the text and combo boxes to the master sizer.
            self.masterSizer.Add(self.texts[i], pos=(i + 1, 0), flag=cbFlag,
                border=10)
            self.masterSizer.Add(self.boxes[i], pos=(i + 1, 1), span=(1, 4),
                flag=cbFlag, border=5)

            # Bind the selection of the combo boxes to an action.
            self.Bind(wx.EVT_COMBOBOX, lambda event, boxNumber=i:
                self.drawNextComboBox(event, boxNumber), self.boxes[i])

        """Initialize the buttons."""
        # Create the open and cancel buttons.
        openButton = wx.Button(self.masterPanel, id=wx.ID_OPEN, label="&Open")
        cancelButton = wx.Button(self.masterPanel, id=wx.ID_CANCEL,
            label="&Cancel")
        openButton.SetFocus()

        # Add the buttons to the master sizer.
        bFlag = wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM
        self.masterSizer.Add(openButton, pos=(5, 0), flag=bFlag, border=10)
        self.masterSizer.Add(cancelButton, pos=(5, 4), flag=bFlag, border=10)

        # Set the bindings for actions when a button is clicked.
        self.Bind(wx.EVT_BUTTON, self.onOpen, openButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelButton)

        """Final frame operations."""
        # Make the sizer dynamic.
        self.masterSizer.AddGrowableCol(2)
        self.masterSizer.AddGrowableRow(0)

        # Set the sizer for the main panel.
        self.masterPanel.SetSizer(self.masterSizer)

        # Set window properties.
        self.SetSize((500, 325))
        self.SetTitle("Open Forecast")
        self.Centre()
        self.Show(True)

    def drawNextComboBox(self, event, boxNumber):
        # Set the next box.
        nextBox = boxNumber + 1

        if self.boxes[boxNumber].GetStringSelection() != "":
            # Show the next text and combo box.
            self.texts[nextBox].Show(True)
            self.boxes[nextBox].Show(True)

            # Get the combo list for the new selection.
            selections = self.getComboList(self.boxes[boxNumber]
                .GetStringSelection())

            # Set the text for the next text.
            self.texts[nextBox].SetLabel(self.tiers[self.currentSelect]
                [nextBox])

            # Set the choices for the next combo box.
            self.boxes[nextBox].SetItems(selections)
        else:
            # When an empty string has been input clear the next text and
            # combo box.
            self.texts[nextBox].Show(False)
            self.boxes[nextBox].Show(False)

        # Do not show any text or combo boxes after the next.
        for i in range(nextBox + 1, 4):
            self.texts[i].Show(False)
            self.boxes[i].Show(False)

        # Relayout the master sizer.
        self.masterSizer.Layout()

    def setSearch(self, event, select):
        # Set the current selection to select.
        self.currentSelect = select

        # Set the selection text to empty for the first combo box.
        self.boxes[0].SetSelection(0)

        # Change the top level text to be what was selected.
        self.texts[0].SetLabel(select)

        # Add the correct choices to the top combo box.
        self.boxes[0].SetItems(self.getComboList(select.lower()))

        # Do not show any text or combo boxes after the first.
        for i in range(1, 4):
            self.texts[i].Show(False)
            self.boxes[i].Show(False)

        # Relayout the master sizer.
        self.masterSizer.Layout()

    def onOpen(self, event):
        print("Opening")

    def onCancel(self, event):
        self.Close()

    def setComboList(self, type):
        pass

    def getComboList(self, source):
        # Initialize list.
        lst = []

        # Pull accounts from data
        with open(source.lower() + ".csv", newline='') as csvFile:
            fileReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in fileReader:
                lst.append(row)

        # Return just the first row.
        lst = lst[0]
        lst.insert(0, "")
        return lst

def main():
    app = wx.App()
    OpenFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
