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
import interfacesql as iface
import os.path
import wx

""" Constant Declarations """
ID_HIERARCHY = 45
ID_VARIABLE = 46

""" Panel Class """
class ManagerPanel(wx.Panel):
    """
    """

    def __init__(self, parent, id):
        """
        To Do:
        1) Find a better way to handle the IDs.
        """

        """Initialize the panel."""
        # Initialize by the parent's constructor.
        super().__init__(parent, -1)

        # Call the initialize user interface method.
        self.id = id

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        """Initialize the combo box."""
        # Get the combo box choices.
        choices = self.getChoices()

        # Create the label and input box.
        self.combo = wx.ComboBox(self, choices=choices,
            style=wx.CB_READONLY)

        # Set the initial selection to be the first item.
        self.combo.SetSelection(0)

        # Bind the combo box selection to a function.
        self.combo.Bind(wx.EVT_COMBOBOX, self.updateList)

        """Initialize the list control."""
        # Create the list control.
        self.itemList = wx.ListCtrl(self, size=(-1, 200),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add the title column.
        self.itemList.InsertColumn(0, "Title", width=500)

        # Bind the selection of an item to a function.
        self.itemList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)
        self.itemList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelected)

        """Initialize the manipulate buttons."""
        # Create the manipulate sizer.
        manipSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        addButton = wx.Button(self, id=wx.ID_ADD)
        self.editButton = wx.Button(self, id=wx.ID_EDIT)
        self.deleteButton = wx.Button(self, id=wx.ID_DELETE)

        # Add the buttons to the manipulate sizer.
        manipSizer.AddMany([addButton, (5, 0), self.editButton, (5, 0),
            self.deleteButton])

        # Bind button presses to functions.
        addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.editButton.Bind(wx.EVT_BUTTON, self.onEdit)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

        """Create any additional key bindings."""
        # Create a new id for selecting all.
        selectAllId = wx.NewId()

        # Bind the id to a function.
        self.Bind(wx.EVT_MENU, self.selectAll, id=selectAllId)

        # Create a new accelerator table and set it to the frame.
        accelT = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("A"), selectAllId)])
        self.SetAcceleratorTable(accelT)

        """Final frame operations."""
        # Add everything to the master sizer.
        masterSizer.AddSpacer(5)
        masterSizer.Add(self.combo, flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(10)
        masterSizer.Add(self.itemList, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=5)
        masterSizer.AddSpacer(10)
        masterSizer.Add(manipSizer, flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(5)

        # Update the list display.
        self.updateList(None)

        # Set the sizer for the master panel.
        self.SetSizer(masterSizer)

    """ Helper Functions """
    def getChoices(self):
        """
        """

        # Pull the possible tiers from the database.
        if self.id == ID_HIERARCHY:
            return iface.getTiers()
        else:
            return iface.getVariables()

    def updateList(self, event):
        """
        """

        # Reset the edit and delete buttons.
        self.editButton.Enable()
        self.deleteButton.SetBackgroundColour(wx.NullColour)

        # Get the list for the selected tier.
        if self.id == ID_HIERARCHY:
            items = iface.getTierList(self.combo.GetStringSelection())
        else:
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

    """ Event Handler Functions """
    def selectAll(self, event):
        """
        """

        # Iterate through the items in the list selecting each.
        for i in range(0, self.itemList.GetItemCount()):
            self.itemList.Select(i)

    def onSelected(self, event):
        """
        """

        # If multiple products are selected, set the edit and delete buttons
        # to be yellow.
        if self.itemList.GetSelectedItemCount() > 1:
            self.editButton.Disable()
            self.deleteButton.SetBackgroundColour("Yellow")
        # If only one product is selected, set the edit and delete buttons
        # to be the default color.
        else:
            self.editButton.Enable()
            self.deleteButton.SetBackgroundColour(wx.NullColour)

    def onAdd(self, event):
        """
        """

        # Create the text entry dialog box.
        dialog = wx.TextEntryDialog(self, "What is the name of the item?",
            "New Item")

        # If OK is not pressed, return false.
        if dialog.ShowModal() != wx.ID_OK:
            return False

        # Get the new item value.
        newItem = dialog.GetValue()

        # If an empty string is input, return false.
        if newItem == "":
            return False

        # Destroy the dialog box.
        dialog.Destroy()

        # Add the inputted text to the database.
        if self.id == ID_HIERARCHY:
            iface.addToTierList(self.combo.GetStringSelection(), newItem)
        else:
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

        # Get the selected combo box item.
        selection = self.combo.GetStringSelection()

        if self.id == ID_HIERARCHY:
            # Remove the altered text from the database.
            iface.removeFromTierList(selection, oldItem)

            # Add the inputted text to the database.
            iface.addToTierList(selection, newItem)
        else:
            # Remove the altered text from the database.
            iface.removeFromVariableList(selection, oldItem)

            # Add the inputted text to the database.
            iface.addToVariableList(selection, newItem)

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

        # Get the number of selected products.
        count = self.itemList.GetSelectedItemCount()

        # Create the delete confimation dialog box.
        confirmDialog = wx.MessageDialog(self,
            "You are about to delete " + str(count) +
            " item(s). Continue?",
            "Delete Confirmation", wx.YES_NO)

        # If no is selected, return false.
        if confirmDialog.ShowModal() != wx.ID_YES:
            return False

        # Remove all selected items.
        selection = self.combo.GetStringSelection()
        for i in range(0, self.itemList.GetSelectedItemCount()):
            # Get the item text.
            item = self.itemList.GetItemText(itemIndex)

            if self.id == ID_HIERARCHY:
                # Remove the selected item.
                iface.removeFromTierList(selection, item)
            else:
                # Remove the selected item.
                iface.removeFromVariableList(selection, item)

            # Get the next selected item index.
            itemIndex = self.itemList.GetNextSelected(itemIndex)

        # Update the list.
        self.updateList(None)

        return True

""" Notebook Class """
class ManagerNotebook(wx.Notebook):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        # Initialize by the parent's constructor.
        super().__init__(*args, **kwargs)

        # Create the hierarchy tab.
        hierarchy = ManagerPanel(self, id=ID_HIERARCHY)

        # Add the hierarchy page to the notebook.
        self.AddPage(hierarchy, "Hierarchy")

        # Create the variable tab.
        variable = ManagerPanel(self, id=ID_VARIABLE)

        # Add the manager page to the notebook.
        self.AddPage(variable, "Input Variable")

        # Bind tab seletion to functions.
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChange)

    """ Event Handler Functions """
    def onPageChange(self, event):
        """
        """

        event.Skip()

""" Frame Class """
class ManagerFrame(wx.Frame):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        """Initialize the frame."""
        # Initialize by the parent's constructor.
        super().__init__(*args, **kwargs)

        # Make a copy of the database file in case the user selects cancel.
        iface.forgeDB()

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        """Initialize the notebook panel."""
        # Create the notebook.
        notebook = ManagerNotebook(masterPanel)

        """Initialize the finish buttons."""
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        applyButton = wx.Button(masterPanel, id=wx.ID_APPLY)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the OK button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([okButton, (5, 0), applyButton, (5, 0),
            cancelButton, (5, 0)])

        # Bind button presses to functions.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        applyButton.Bind(wx.EVT_BUTTON, self.onApply)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        """Final frame operations."""
        # Add everything to the master sizer.
        masterSizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        masterSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT)
        masterSizer.AddSpacer(5)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Bind closing the frame to a function.
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set window properties.
        self.Centre()
        self.Show(True)

    """ Event Handler Functions """
    def onOK(self, event):
        """
        """

        # Remove the unaltered version of the database file.
        iface.removeDB()

        # Close the window.
        self.Close()

    def onApply(self, event):
        """
        """

        # Reforge the database file.
        iface.forgeDB()

    def onCancel(self, event):
        """
        """

        # Replace the database file with the unaltered version.
        iface.replaceDB()

        # Close the window.
        self.Close()

    def onClose(self, event):
        """
        """

        # Replace the database file with the unaltered version, if it exists.
        if os.path.isfile("../../data/temp.h5"):
            iface.replaceDB()

        # Destroy the window.
        self.Destroy()

def main():
    """
    """

    app = wx.App()
    ManagerFrame(None, title="Data Manager", size=(600, 400),
        style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
