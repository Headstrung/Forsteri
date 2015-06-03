"""
Assign Missing Items Frame

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

# Import python modules.
import sqlite3
import wx

# Import forsteri modules.
from forsteri.interface import sql as isql

class AssignFrame(wx.Frame):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        ## Frame
        # Initialize the parents constructor.
        super(AssignFrame, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Open a connection to the database.
        self.connection = sqlite3.connect(isql.MASTER)

        ## Missing List
        # Create the missing list control.
        self.missingList = wx.ListCtrl(masterPanel,
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.missingList.InsertColumn(0, "Sku", width=250)

        # Bind the selection of an item to a function.
        self.missingList.Bind(wx.EVT_LEFT_DCLICK, self.onAssign)

        ## Button
        # Create the assign button.
        assignButton = wx.Button(masterPanel, label="Assign")

        # Bind the button to a function.
        assignButton.Bind(wx.EVT_BUTTON, self.onAssign)

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

        ## Frame Operations
        # Add everything to the master sizer.
        masterSizer.AddSpacer(10)
        masterSizer.Add(self.missingList,
            flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=5)
        masterSizer.Add(assignButton, flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(9)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(290, 2)),
            flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(9)
        masterSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM,
            border=5)

        # Populate the list.
        self.updateList()

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Bind closing the frame to a function.
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set window properties.
        self.SetSize((300, 302))
        self.SetTitle("Assign Missing Products")
        self.Centre()
        self.Show(True)


    """
    Helper Functions
    """
    def updateList(self):
        """
        """

        # Get the missing values from the database.
        missing = isql.getMissing(self.connection)

        # Remove all items from the list control.
        self.missingList.DeleteAllItems()

        # Iterate over the missing values and add the skus to the list.
        index = 0
        for row in missing:
            self.missingList.InsertStringItem(index, row[1])
            index += 1

    """
    Event Handlers
    """
    def onAssign(self, event):
        """
        """

        # Get the selected sku.
        skuIndex = self.missingList.GetFirstSelected()

        # Check if a sku has been selected.
        if skuIndex == -1:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Get the sku value.
        sku = self.missingList.GetItemText(skuIndex)

        # Create the text entry dialog box.
        dialog = wx.TextEntryDialog(self,
            "Assign " + sku + " to what product?", "Assign Product")

        # If OK is not pressed, return false.
        if dialog.ShowModal() != wx.ID_OK:
            return False

        # Get the new item value.
        product = dialog.GetValue()

        # If an empty string is input, return false.
        if product == "":
            return False

        # Destroy the dialog box.
        dialog.Destroy()

        # Check if the sku is already defined.
        productData = isql.getProductData(product, self.connection)
        if productData[2] is not None:
            overDialog = wx.MessageDialog(self, product +\
                " is already assigned the sku " + productData[2] +\
                ". Would you like to overwrite?", "Overwrite",
                wx.YES_NO|wx.ICON_QUESTION)
            if overDialog.ShowModal() == wx.ID_NO:
                return False

        # Assign the missing sku the correct product code.
        isql.assignMissing(product, sku, self.connection)

    def onOK(self, event):
        """
        """

        # Commit the changes to the database.
        self.connection.commit()

        self.Close()

    def onCancel(self, event):
        """
        """

        self.Close()

    def onClose(self, event):
        """
        """

        # Close the database connection.
        self.connection.close()

        self.Destroy()

if __name__ == '__main__':
    app = wx.App()
    AssignFrame(None, style=wx.DEFAULT_FRAME_STYLE)#^wx.RESIZE_BORDER)
    app.MainLoop()
