#!/usr/bin/python

"""
Variable Manager Frame

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

        # Make a copy of the database file in case the user selects cancel.
        iface.forgeDB()

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        """Initialize the hierarchy combo box."""
        # Create the hierarchy sizer.
        hierSizer = wx.BoxSizer(wx.VERTICAL)

        # Get the combo box choices.
        choices = self.getChoices()

        # Create the label and input box.
        label = wx.StaticText(masterPanel, label="Variable:")
        self.combo = wx.ComboBox(masterPanel, choices=choices,
            style=wx.CB_READONLY)

        # Set the initial selection to be the fist item.
        self.combo.SetSelection(0)

        # Add the label and combo box to the hierarchy sizer.
        hierSizer.AddMany([label, (0, 5), self.combo])

        # Bind the combo box selection to a function.
        self.combo.Bind(wx.EVT_COMBOBOX, self.updateList)

        """Initialize the list control."""
        # Create the list control.
        self.itemList = wx.ListCtrl(masterPanel, size=(-1, 200),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add the title column.
        self.itemList.InsertColumn(0, "Title", width=500)

        # Update the list display.
        self.updateList(None)

        """Initialize the manipulate buttons."""
        # Create the manipulate sizer.
        manipSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        addButton = wx.Button(masterPanel, id=wx.ID_ADD)
        editButton = wx.Button(masterPanel, id=wx.ID_EDIT)
        deleteButton = wx.Button(masterPanel, id=wx.ID_DELETE)

        # Add the buttons to the manipulate sizer.
        manipSizer.AddMany([addButton, (5, 0), editButton, (5, 0),
            deleteButton])

        # Bind button presses to functions.
        addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        editButton.Bind(wx.EVT_BUTTON, self.onEdit)
        deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

        """Initialize the finish buttons."""
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the OK button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([okButton, (5, 0), cancelButton, (5, 0)])

        # Bind button presses to functions.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        """Final frame operations."""
        # Add everything to the master sizer.
        masterSizer.AddSpacer(5)
        masterSizer.Add(hierSizer, flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(10)
        masterSizer.Add(self.itemList, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=5)
        masterSizer.AddSpacer(10)
        masterSizer.Add(manipSizer, flag=wx.ALIGN_CENTER)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(580, 20)),
            flag=wx.ALIGN_CENTER)
        masterSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT)
        masterSizer.AddSpacer(5)

        # Set the sizer for the main panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((600, 390))
        self.SetTitle("Input Variable Manager")
        self.Centre()
        self.Show(True)

    def getChoices(self):
        """
        """

        # Pull the possible variables from the database.
        return iface.getVariables()

    def updateList(self, event):
        """
        """

        # Get the list for the selected variable.
        items = iface.getVariableList(self.combo.GetStringSelection())

        # Sort the list.
        items.sort()

        # Remove all items from the list control and reset the index.
        self.itemList.DeleteAllItems()

        # Add the items to the list control.
        index = 0
        for item in items:
            self.itemList.InsertItem(index, item)
            index += 1

        return True

    def onAdd(self, event):
        """
        """

        # Create the text entry dialog box.
        dialog = wx.TextEntryDialog(self, "What is the name of the item?",
            "New Item")

        # If OK is not pressed, return false.
        if dialog.ShowModal() != wx.ID_OK:
            return False

        # Get the new item value
        newItem = dialog.GetValue()

        # If an empty string is input, return false.
        if newItem == "":
            return False

        # Destroy the dialog box.
        dialog.Destroy()

        # Add the inputted text to the database.
        iface.addToVariableList(self.combo.GetStringSelection(), newItem)

        # Update the list.
        self.updateList(None)

        return True

    def onEdit(self, event):
        """
        """

        # Get the selected item index from the list.
        itemIndex = self.itemList.GetFirstSelected()

        # Send an error if nothing is selected.
        if itemIndex == -1:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Get the string value of the old item.
        oldItem = self.itemList.GetItemText(itemIndex)

        # Create the text entry dialog box.
        dialog = wx.TextEntryDialog(self, "What is the name of the item?",
            "Edit Item", oldItem)

        # If OK is not pressed, return false.
        if dialog.ShowModal() != wx.ID_OK:
            return False

        # Get the new item value.
        newItem = dialog.GetValue()

        # If an empty string is input or there is no change, return false.
        if newItem == "" or newItem == oldItem:
            return False

        # Destroy the dialog box.
        dialog.Destroy()

        # Remove the altered text from the database.
        variable = self.combo.GetStringSelection()
        iface.removeFromVariableList(variable, oldItem)

        # Add the inputted text to the database.
        iface.addToVariableList(variable, newItem)

        # Update the list.
        self.updateList(None)

        return True

    def onDelete(self, event):
        """
        """

        # Get the first selected item index from the list.
        itemIndex = self.itemList.GetFirstSelected()

        # Send an error if nothing is selected.
        if itemIndex == -1:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Remove all selected items.
        variable = self.combo.GetStringSelection()
        for i in range(0, self.itemList.GetSelectedItemCount()):
            # Get the item text.
            item = self.itemList.GetItemText(itemIndex)

            # Remove the selected item.
            iface.removeFromVariableList(variable, item)

            # Get the next selected item index.
            itemIndex = self.itemList.GetNextSelected(itemIndex)

        # Update the list.
        self.updateList(None)

        return True

    def onOK(self, event):
        """
        """

        # Remove the unaltered version of the database file.
        iface.removeDB()

        self.Close()

    def onCancel(self, event):
        """
        """

        # Replace the database file with the unaltered version.
        iface.replaceDB()

        self.Close()

""" Start Application """
def main():
    """
    """

    app = wx.App()
    ManagerFrame(None, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
