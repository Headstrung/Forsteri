#!/usr/bin/python

"""
Data Manager Frame

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
import sqlite3
import wx

from forsteri.interface import sql as isql

"""
Constant Declarations
"""
ID_HIERARCHY = 45
ID_VARIABLE = 46

"""
Panel Class
"""
class ManagerPanel(wx.Panel):
    """
    A panel that contains a combo box selection and a list control. This is
    allows for adding, editing, and deleting some variable held in the HDF5
    file.

    Extends:
      wx.Panel
    """

    def __init__(self, id, connection, *args, **kwargs):
        """
        Initialize the panel.

        Args:
          parent (wx.Frame): The associated parent for this panel.
          id (int): The ID for the panel which defines what will be edited.
            This can currently be ID_HIERARCHY or ID_VARIABLE. As the software
            expands, so will the possibilities.
          connection (sqlite3.Connection): A connection to the database.

        Returns:
          ManagerPanel

        To Do:
          Find a better way to handle the IDs.
        """

        ## Panel
        # Initialize by the parent's constructor.
        super(ManagerPanel, self).__init__(*args, **kwargs)

        # Set the ID for the panel.
        self.id = id

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Create a static connection.
        self.connection = connection

        ## Combo Box
        # Get the combo box choices.
        choices = self.getChoices()

        # Create the label and input box.
        self.combo = wx.ComboBox(self, choices=choices,
            style=wx.CB_READONLY|wx.CB_SORT)

        # Set the initial selection to be the first item.
        self.combo.SetSelection(0)

        # Bind the combo box selection to a function.
        self.combo.Bind(wx.EVT_COMBOBOX, self.updateList)

        ## List Control
        # Create the list control.
        self.itemList = wx.ListCtrl(self, size=(-1, 200),
            style=wx.BORDER_SUNKEN|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)

        # Add the title column.
        self.itemList.InsertColumn(0, "Title", width=500)

        # Bind the selection of an item to a function.
        self.itemList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)
        self.itemList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelected)
        self.itemList.Bind(wx.EVT_LEFT_DCLICK, self.onEdit)

        ## Manipulate Buttons
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

        ## Key Bindings
        # Create a new id for selecting all.
        selectAllId = wx.NewId()

        # Bind the id to a function.
        self.Bind(wx.EVT_MENU, self.selectAll, id=selectAllId)

        # Create a new accelerator table and set it to the frame.
        accelT = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("A"), selectAllId)])
        self.SetAcceleratorTable(accelT)

        ## Frame Operations
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

    """
    Helper Functions
    """
    def getChoices(self):
        """
        Get the combo box choices depending on the ID.

        Args:
          None

        Returns:
          list of str: The possible choices for the combo box with regard to
            the defined ID.
        """

        # Pull the possible tiers from the database.
        if self.id == ID_HIERARCHY:
            return isql.getTiers(self.connection)
        else:
            return isql.getVariables(self.connection)

    """
    Event Handler Functions
    """
    def updateList(self, event):
        """
        Update the items displayed in the list control.

        Args:
          event (wx._core.CommandEvent): The triggered event after completing
            some action that would alter the items in the list control.

        Returns:
          None
        """

        # Reset the edit and delete buttons.
        self.editButton.Enable()
        self.deleteButton.SetBackgroundColour(wx.NullColour)

        # Get the list for the selected tier.
        if self.id == ID_HIERARCHY:
            items = isql.getForTier(self.combo.GetStringSelection(),
                self.connection)
        else:
            items = isql.getForVariable(self.combo.GetStringSelection(),
                self.connection)

        # Sort the items in ascending order.
        items.sort()

        # Remove all items from the list control.
        self.itemList.DeleteAllItems()

        # Add the items to the list control.
        index = 0
        for item in items:
            self.itemList.InsertStringItem(index, item)
            index += 1

    def selectAll(self, event):
        """
        What to do when the "Ctrl+A" button combination is entered. Select
        all items in the list control.

        Args:
          event (wx._core.CommandEvent): The triggered event after the button
            combo "Ctrl+A" is entered.

        Returns:
          None
        """

        # Iterate through the items in the list selecting each.
        for i in range(0, self.itemList.GetItemCount()):
            self.itemList.Select(i)

    def onSelected(self, event):
        """
        What to do when items in the list control are selected. Reset the
        color of the buttons if only one item is selected. If multiple items
        are selected, disable the edit button and set the delete button to be
        yellow.

        Args:
          event (wx._core.CommandEvent): The triggered event after an item in
            the list control is selected.

        Returns:
          None
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
        What to do when the add button is pressed. Open the text entry dialog
        and obtain the title of the new item. Write the new item into the HDF5
        file.

        Args:
          event (wx._core.CommandEvent): The triggered event when the add
            button is pressed.

        Returns:
          None
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
            isql.addTitle(self.combo.GetStringSelection(), newItem,
                self.connection)
        else:
            isql.addAlias(self.combo.GetStringSelection(), newItem,
                self.connection)

        # Update the list.
        self.updateList(None)

    def onEdit(self, event):
        """
        What to do when the edit button is pressed. Open the text entry
        dialog and fill it with what the current title is. Obtain the altered
        title for the item. Write the altered item into the HDF5 file.

        Args:
          event (wx._core.CommandEvent): The triggered event when the edit
            button is pressed.

        Returns:
          None
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
            # Set the new item in the database.
            isql.setTitle(selection, oldItem, newItem, self.connection)
        else:
            # Set the new item in the database.
            isql.setAlias(selection, oldItem, newItem, self.connection)

        # Update the list.
        self.updateList(None)

    def onDelete(self, event):
        """
        What to do when the delete button is pressed. Remove the selected item
        in the list control from the HDF5 file.

        Args:
          event (wx._core.CommandEvent): The triggered event when the delete
            button is pressed.

        Returns:
          None
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
                isql.removeTitle(selection, item, self.connection)
            else:
                # Remove the selected item.
                isql.removeAlias(selection, item, self.connection)

            # Get the next selected item index.
            itemIndex = self.itemList.GetNextSelected(itemIndex)

        # Update the list.
        self.updateList(None)

"""
Notebook Class
"""
class ManagerNotebook(wx.Notebook):
    """
    A notebook that holds the possible panels.

    Extends:
      wx.Notebook
    """

    def __init__(self, connection, *args, **kwargs):
        """
        Initialize the notebook.

        Args:
          *args (): Any arguments to be passed directly to the super's
            constructor.
          **kwargs (): Any keyword arguments to be passed to the super's
            constructor.

        Returns:
          ManagerNotebook
        """

        # Initialize by the parent's constructor.
        super(ManagerNotebook, self).__init__(*args, **kwargs)

        # Create the hierarchy tab.
        hierarchy = ManagerPanel(ID_HIERARCHY, connection, self)

        # Add the hierarchy page to the notebook.
        self.AddPage(hierarchy, "Hierarchy")

        # Create the variable tab.
        variable = ManagerPanel(ID_VARIABLE, connection, self)

        # Add the manager page to the notebook.
        self.AddPage(variable, "Input Variable")

        # Bind tab seletion to functions.
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChange)

    """
    Event Handler Functions
    """
    def onPageChange(self, event):
        """
        What to do when a new page has been selected.

        Args:
          event (wx._core.CommandEvent): The triggered event when a new page
            is selected.

        Returns:
          None
        """

        # Skip the event.
        event.Skip()

"""
Frame Class
"""
class ManagerFrame(wx.Frame):
    """
    The frame that contains the notebook and all panels. The "OK", "Apply",
    and "Cancel" buttons are housed here.

    Extends:
      wx.Frame
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the frame.

        Args:
          *args (): Any arguments to be passed directly to the super's
            constructor.
          **kwargs (): Any keyword arguments to be passed to the super's
            constructor.

        Returns:
          ManagerFrame
        """

        """Initialize the frame."""
        # Initialize by the parent's constructor.
        super(ManagerFrame, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Open a connection to the database.
        self.connection = sqlite3.connect(isql.MASTER)

        """Initialize the notebook panel."""
        # Create the notebook.
        notebook = ManagerNotebook(self.connection, masterPanel)

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
        self.SetSize((600, 400))
        self.SetTitle("Data Manager")
        self.Centre()
        self.Show(True)

    """
    Event Handler Functions
    """
    def onOK(self, event):
        """
        What to do when the OK button has been pressed. Remove the HDF5 copy
        file from the filesystem.

        Args:
          event (wx._core.CommandEvent): The triggered event when a new page
            is selected.

        Returns:
          None
        """

        # Commit and close the database.
        self.connection.commit()
        self.connection.close()

        # Close the window.
        self.Close()

    def onApply(self, event):
        """
        What to do when the Apply button has been pressed. Make a new copy of
        the HDF5 file in the filesystem.

        Args:
          event (wx._core.CommandEvent): The triggered event when a new page
            is selected.

        Returns:
          None
        """

        # Commit the database.
        self.connection.commit()

    def onCancel(self, event):
        """
        What to do when the Cancel button has been pressed. Replace the HDF5
        file with the copy made in the filesystem.

        Args:
          event (wx._core.CommandEvent): The triggered event when a new page
            is selected.

        Returns:
          None
        """

        # Close the database.
        self.connection.close()

        # Close the window.
        self.Close()

    def onClose(self, event):
        """
        What to do when the frame is closed. If a copy still exists, replace
        the HDF5 file with the copy in the filesystem.

        Args:
          event (wx._core.CommandEvent): The triggered event when a new page
            is selected.

        Returns:
          None
        """

        # Close the database.
        self.connection.close()

        # Destroy the window.
        self.Destroy()

def main():
    """
    When the file is called independently create and display the manager frame.
    """

    app = wx.App()
    ManagerFrame(None, title="Data Manager", size=(600, 400),
        style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
