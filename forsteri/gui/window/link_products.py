#!/usr/bin/python

"""
Link Products Frame

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
import threading as td
import wx

from forsteri.interface import data as idata
from forsteri.interface import sql as isql

"""
Constant Declarations
"""


"""
Frame Class
"""
class LinkFrame(wx.Frame):
    """
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
          LinkFrame
        """

        ## Frame
        # Initialize by the parent's constructor.
        super(LinkFrame, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## List Control
        # Create the list control.
        self.linkList = wx.ListCtrl(masterPanel, size=(300, 200),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.linkList.InsertColumn(0, "Old", width=145)
        self.linkList.InsertColumn(1, "New", width=145)

        # Bind the selection of an item to a function.
        self.linkList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)
        self.linkList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelected)
        self.linkList.Bind(wx.EVT_LEFT_DCLICK, self.onEdit)

        ## Manipulate Buttons
        # Create the manipulate sizer.
        manipSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        self.addButton = wx.Button(masterPanel, id=wx.ID_ADD)
        self.editButton = wx.Button(masterPanel, id=wx.ID_EDIT)
        self.deleteButton = wx.Button(masterPanel, id=wx.ID_DELETE)

        # Add the buttons to the manipulate sizer.
        manipSizer.AddMany([self.addButton, (5, 0), self.editButton, (5, 0),
            self.deleteButton])

        # Bind button presses to functions.
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.editButton.Bind(wx.EVT_BUTTON, self.onEdit)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

        ## Finish Buttons
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the ok button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([okButton, (5, 0), cancelButton])

        # Bind the button presses to function.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

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
        masterSizer.AddSpacer(10)
        masterSizer.Add(self.linkList, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,
            border=5)
        masterSizer.Add(manipSizer, flag=wx.TOP|wx.ALIGN_CENTER, border=10)
        masterSizer.AddSpacer(9)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(312, 2)),
            flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(9)
        masterSizer.Add(finishSizer, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT,
            border=5)

        # Open a connection to the database.
        self.connection = sqlite3.connect(isql.MASTER)
        self.connection2 = sqlite3.connect(idata.MASTER)

        # Update the displayed list.
        self.initializeList(None)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Bind closing the frame to a function.
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set window properties.
        self.SetSize((328, 333))
        self.SetTitle("Link Products")
        self.Centre()
        self.Show(True)

    """
    Event Handlers
    """
    def initializeList(self, event):
        """
        """

        # Get the list of links.
        links = isql.getLinks(self.connection)

        # Iterate over the list and add each to the control.
        index = 0
        for (old, new) in links:
            # Add the items to the list control.
            self.linkList.InsertStringItem(index, old)
            self.linkList.SetStringItem(index, 1, new)

            # Increment the index.
            index += 1

    def updateList(self, event):
        """
        """

        # Get the list of links.
        links = isql.getLinks(self.connection)

        # Remove all items from the list control.
        self.linkList.DeleteAllItems()

        # Update the selected colors.
        self.onSelected(event)

        # Iterate over the list and add each to the control.
        index = 0
        for (old, new) in links:
            # Add the items to the list control.
            self.linkList.InsertItem(index, old)
            self.linkList.SetItem(index, 1, new)

            # Increment the index.
            index += 1

    def onSelected(self, event):
        """
        """

        # If multiple products are selected, set the edit and delete buttons
        # to be yellow.
        if self.linkList.GetSelectedItemCount() > 1:
            self.editButton.Disable()
            self.deleteButton.SetBackgroundColour("Yellow")
        # If only one product is selected, set the edit and delete buttons
        # to be the default color.
        else:
            self.editButton.Enable()
            self.deleteButton.SetBackgroundColour(wx.NullColour)

    def selectAll(self, event):
        """
        """

        # Iterate through the items in the list selecting each.
        for i in range(0, self.linkList.GetItemCount()):
            self.linkList.Select(i)

    def onAdd(self, event):
        """
        """

        # Create the dialog box.
        linkDlg = LinkDialog(self, title="Add Link")

        # Show the link dialog box.
        if linkDlg.ShowModal() == wx.ID_CANCEL:
            return

        # Get the selections from the dialog boxes.
        (old, new) = linkDlg.getSelection()

        # Destroy the dialog box.
        linkDlg.Destroy()

        # If either input is an empty string, show an error.
        if old == '' or new == '':
            errorDialog = wx.MessageDialog(self,
                "One of the entries was empty.", "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Add the link to the database.
        isql.addLink(old, new, self.connection)

        # Add the data link.
        idata.linkData(old, new, self.connection2)

        # Update the link list.
        self.updateList(event)

    def onEdit(self, event):
        """
        """

        # Create the dialog box.
        linkDlg = LinkDialog(self, title="Add Link")

        # Get the selected data.
        index = self.linkList.GetFirstSelected()

        # If nothing is selected, send an error.
        if index == -1:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Get the string value of the old product.
        old1 = self.linkList.GetItemText(index)
        new1 = self.linkList.GetItemText(index, 1)

        # Set the text in the link dialog.
        linkDlg.setSelection(old1, new1)

        # Show the link dialog box.
        if linkDlg.ShowModal() == wx.ID_CANCEL:
            return

        # Get the selections from the dialog boxes.
        (old2, new2) = linkDlg.getSelection()

        # Destroy the dialog box.
        linkDlg.Destroy()

        # If either input is an empty string, show an error.
        if old2 == '' or new2 == '':
            errorDialog = wx.MessageDialog(self,
                "One of the entries was empty.", "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Edit the link in the database.
        if old1 == old2 and new1 == new2:
            pass
        elif old1 != old2 and new1 == new2:
            isql.setLink(old2, new2, 1, self.connection)
            idata.unlinkData(old1, new1, self.connection2)
            idata.linkData(old2, new2, self.connection2)
        elif old1 == old2 and new1 != new2:
            isql.setLink(old2, new2, 2, self.connection)
            idata.unlinkData(old1, new1, self.connection2)
            idata.linkData(old2, new2, self.connection2)
        else:
            isql.setLink(old2, new2, old1, self.connection)
            idata.unlinkData(old1, new1, self.connection2)
            idata.linkData(old2, new2, self.connection2)

        # Update the link list
        self.updateList(event)

    def onDelete(self, event):
        """
        """

        # Get the selected data.
        index = self.linkList.GetFirstSelected()

        # If nothing is selected, send an error.
        if index == -1:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return False

        # Get the string value of the old product.
        old = self.linkList.GetItemText(index)
        new = self.linkList.GetItemText(index, 1)

        # Iterate until all selected are removed.
        run = True
        while run:
            # Remove the link from the database.
            isql.removeLink(old, new, self.connection)

            # Remove the data link.
            idata.unlinkData(old, new, self.connection2)

            # Get the next index.
            index = self.linkList.GetNextSelected(index)

            # If there is no next index stop the loop.
            if index == -1:
                run = False
            else:
                old = self.linkList.GetItemText(index)
                new = self.linkList.GetItemText(index, 1)

        # Update the link list.
        self.updateList(event)

    def onOK(self, event):
        """
        """

        # Commit and close the database.
        self.connection.commit()
        self.connection.close()
        self.connection2.commit()
        self.connection2.close()

        self.Close()

    def onCancel(self, event):
        """
        """

        # Close the database.
        self.connection.close()
        self.connection2.close()

        self.Close()

    def onClose(self, event):
        """
        """

        self.Destroy()

"""
"""
class LinkDialog(wx.Dialog):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        # Initialize by the parent's constructor.
        super(LinkDialog, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the box sizers.
        oldSizer = wx.BoxSizer(wx.HORIZONTAL)
        newSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the static text.
        oldLabel = wx.StaticText(masterPanel, label="Old Product")
        newLabel = wx.StaticText(masterPanel, label="New Product")

        # Create the old and new text entries.
        self.oldEntry = wx.TextCtrl(masterPanel, size=(150, -1))
        self.newEntry = wx.TextCtrl(masterPanel, size=(150, -1))

        # Add the label and entries to the sizers.
        oldSizer.AddMany([oldLabel, (5, 0), self.oldEntry])
        newSizer.AddMany([newLabel, (5, 0), self.newEntry])

        # Get the choices for auto complete.
        links = self.getChoices()

        # Set the auto complete for the text entries.
        self.oldEntry.AutoComplete(links)
        self.newEntry.AutoComplete(links)

        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the finish buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the OK button to be the dafault button.
        okButton.SetDefault()

        # Add the finish buttons to the sizer.
        finishSizer.AddMany([okButton, (5, 0), cancelButton])

        # Add the text and combo box to the sizer.
        masterSizer.AddSpacer(10)
        masterSizer.Add(oldSizer, flag=wx.LEFT|wx.BOTTOM|wx.RIGHT|
            wx.ALIGN_RIGHT, border=5)
        masterSizer.Add(newSizer, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_RIGHT,
            border=5)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(240, 20)),
            flag=wx.ALIGN_CENTER)
        masterSizer.Add(finishSizer, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT,
            border=5)

        # Set the master sizer.
        masterPanel.SetSizer(masterSizer)

        # Set the size of the window.
        self.SetSize((250, 150))

    def getChoices(self):
        """
        """

        # Get the list of variables.
        links = isql.getAttribute("product")

        # Extract only the first column.
        links = [link[0] for link in links]

        return links

    def getSelection(self):
        """
        """

        # Get the value of the text entries.
        old = self.oldEntry.GetValue()
        new = self.newEntry.GetValue()

        return old, new

    def setSelection(self, old, new):
        """
        """

        # Set the value of the text entries.
        self.oldEntry.SetValue(old)
        self.newEntry.SetValue(new)

        return True

"""
Start Application
"""
def main():
    """
    When the file is called independently create and display the manager frame.
    """

    app = wx.App()
    LinkFrame(None, style=wx.DEFAULT_FRAME_STYLE)#^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
