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
    To Do:
      Make the header clickable and sort by that column when clicked.
      Add a mass add function through a button/menu or something.

    To Do Far:
      Add ways to search for products. Being by chemical, component, container.
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
        masterSizer = wx.BoxSizer(wx.HORIZONTAL)

        """Initialize the search by section."""
        # Create the search by static box.
        searchSB = wx.StaticBox(masterPanel, label="Search by")

        # Create the search sizer.
        searchSizer = wx.StaticBoxSizer(searchSB, wx.VERTICAL)

        # Create the name type sizer.
        ntSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the name type radio buttons.
        self.productRB = wx.RadioButton(masterPanel, label="Product",
            style=wx.RB_GROUP)
        skuRB = wx.RadioButton(masterPanel, label="Sku")

        # Add the name type radio buttons to the name type sizer.
        ntSizer.AddMany([self.productRB, (25, 0), skuRB])

        # Get the label strings and combo box choices.
        self.labelStrings = ["Account", "Class", "Category", "Subcategory"]
        choices = self.getChoices()

        # Create the labels and input boxes.
        labels = [None] * 4
        self.inputs = [None] * 5

        # Create the text entry for the name.
        self.inputs[0] = wx.TextCtrl(masterPanel, size=(150, -1))

        # Add the name type and text entry to the search sizer.
        searchSizer.AddMany([(0, 10), ntSizer, (0, 5), self.inputs[0]])

        # Bind text entry to a function.
        self.inputs[0].Bind(wx.EVT_TEXT, self.updateList)

        # Create subsequent label and combo boxes, add them to the search
        # sizer, and bind them to functions.
        for i in range(0, 4):
            labels[i] = wx.StaticText(masterPanel, label=self.labelStrings[i])
            self.inputs[i + 1] = wx.ComboBox(masterPanel,
                choices=choices[i], style=wx.CB_READONLY|wx.CB_SORT)
            searchSizer.AddMany([(0, 10), labels[i], (0, 5),
                self.inputs[i + 1]])
            self.inputs[i + 1].Bind(wx.EVT_COMBOBOX, self.updateList)

        """Initialize the selection section"""
        # Create the selection sizer.
        selectSizer = wx.BoxSizer(wx.VERTICAL)

        """Initialize the list control."""
        # Create the list control.
        self.productList = wx.ListCtrl(masterPanel, size=(-1, 400),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.productList.InsertColumn(0, "Product", width=136)
        self.productList.InsertColumn(1, "Account", width=136)
        self.productList.InsertColumn(2, "Class", width=136)
        self.productList.InsertColumn(3, "Category", width=136)
        self.productList.InsertColumn(4, "Subcategory", width=136)

        # Update the displayed list.
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
        reportButton = wx.Button(masterPanel, label="&Report")
        openButton = wx.Button(masterPanel, id=wx.ID_OPEN)
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the open button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([reportButton, (5, 0), openButton, (5, 0),
            okButton, (5, 0), cancelButton, (5, 0)])

        # Bind the button presses to function.
        reportButton.Bind(wx.EVT_BUTTON, self.onReport)
        openButton.Bind(wx.EVT_BUTTON, self.onOpen)
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        """Create any additional key bindings."""
        # Create a new id for selecting all.
        selectAllId = wx.NewId()

        # Bind the id to a function.
        self.Bind(wx.EVT_MENU, self.selectAll, id=selectAllId)

        # Create a new accelerator table and set it to the frame.
        accelT = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("A"), selectAllId)])
        self.SetAcceleratorTable(accelT)

        """Final frame operations."""
        # Add the items to the selection sizer.
        selectSizer.Add(self.productList,
            flag=wx.LEFT|wx.RIGHT|wx.TOP, border=5)
        selectSizer.AddSpacer(10)
        selectSizer.Add(manipSizer, flag=wx.ALIGN_CENTER)
        selectSizer.Add(wx.StaticLine(masterPanel, size=(680, 20)),
            flag=wx.ALIGN_CENTER)
        selectSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT)
        selectSizer.AddSpacer(5)

        # Add everything to the master sizer.
        masterSizer.Add((5, 0))
        masterSizer.Add(searchSizer, flag=wx.ALIGN_TOP|wx.EXPAND)
        masterSizer.Add(selectSizer, flag=wx.EXPAND)

        # Set the sizer for the main panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((860, 532))
        self.SetTitle("Open/Manage Products")
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

        # Switch the indices of category and class.
        connect[1], connect[2] = connect[2], connect[1]

        return connect

    def updateList(self, event):
        """
        To Do:
          Check which implementation is faster between match and product.
          Implement the search functionality (possibly in another function).
        """

        """Get match implementation."""

        # Get the lists of data from the database.
        data = [iface.getMatch("product")]
        for label in self.labelStrings:
            data.append(iface.getMatch(label))

        # Remove all items from the list control and reset the index.
        self.productList.DeleteAllItems()
        index = 0

        # Add the items to the list control.
        for j in range(0, len(data[0])):
            self.productList.InsertItem(index, data[0][j])
            self.productList.SetItem(index, 1, data[1][j])
            self.productList.SetItem(index, 2, data[2][j])
            self.productList.SetItem(index, 3, data[3][j])
            self.productList.SetItem(index, 4, data[4][j])
            index += 1

        return True

        """Get product implementation."""

        """Search feature to be implemented."""

        #product = self.productRB.GetValue()

        # Initialize a final list for all matched inputs.
        matchedFinal = []

        # Iterate over the possible combo box inputs.
        for i in range(1, 5):
            # Get the selection of the combo box.
            selected = self.inputs[i].GetStringSelection()

            # If there is a selection continue.
            if selected != "":
                # Extract the values for each product.
                allValues = iface.getMatch(self.labelStrings[i - 1])

                # Initialize a list to hold individual matched indices.
                matched = []

                # Iterate over all values pulled from the database.
                for value in allValues:
                    # Check for matched values.
                    if value == selected:
                        # Append finds to the list.
                        matched.append(allValues.index(value))

                # Append all finds to the final list of matched combo box
                # inputs.
                matchedFinal.append(set(matched))

        # Check if the final matched length is greater than 0.
        if len(matchedFinal) > 0:
            # If so, use the first set of indices as the base.
            final = matchedFinal[0]

            # Iterate over the entire length and find the intersection.
            for j in range(1, len(matchedFinal)):
                final = final & matchedFinal[j]

            print(final)

        return True

    def selectAll(self, event):
        """
        """

        # Iterate through the items in the list selecting each.
        for i in range(0, self.productList.GetItemCount()):
            self.productList.Select(i)

        return True

    def onAdd(self, event):
        """
        """

        # Create the custom text entry dialog box.
        addDialog = InputDialog(self, title="Add Product", size=(300, 275))

        # If OK is pressed get the text, otherwise return false.
        if addDialog.ShowModal() == wx.ID_OK:
            addProductData = addDialog.getTextEntry()

            # If an empty string is input for product send an error.
            if addProductData[0] == "":
                errorDialog = wx.MessageDialog(self,
                    "Product cannot be empty.", "Error", wx.OK|wx.ICON_ERROR)
                errorDialog.ShowModal()
                return False
        else:
            return False

        # Destroy the dialog box.
        addDialog.Destroy()

        # Add the inputted product data to the database.
        iface.addProduct(addProductData[0], addProductData[1],
            addProductData[2], addProductData[3], addProductData[4],
            addProductData[5])

        # Update the list.
        self.updateList(None)

        return True

    def onEdit(self, event):
        """
        """

        # Check if multiple items are selected.
        selectCount = self.productList.GetSelectedItemCount()

        # Pass to the multi function if more than one item is selected.
        if selectCount > 1:
            self.onEditMulti(selectCount)
            return False
        # Send an error if nothing is selected.
        elif selectCount == 0:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Get the selected item index from the list.
        productIndex = self.productList.GetFirstSelected()

        # Get the string value of the old product.
        product = self.productList.GetItemText(productIndex)

        # Extract the attributes from the database.
        oldProductData = iface.getProduct(product)

        # Create the custom text entry dialog box.
        editDialog = InputDialog(self, title="Edit Product", size=(300, 275))

        # Set the initial text to be the old product.
        editDialog.setTextEntry(oldProductData)

        # If OK is pressed get the data, otherwise return false.
        if editDialog.ShowModal() == wx.ID_OK:
            newProductData = editDialog.getTextEntry()

            # If an empty string is input for product send an error.
            if newProductData[0] == "":
                errorDialog = wx.MessageDialog(self,
                    "Product cannot be empty.", "Error", wx.OK|wx.ICON_ERROR)
                errorDialog.ShowModal()
                return False
        else:
            return False

        # Destroy the dialog box.
        editDialog.Destroy()

        # Remove the altered product from the databse.
        iface.removeProduct(product)

        # Add the inputted product data to the database.
        iface.addProduct(newProductData[0], newProductData[1],
            newProductData[2], newProductData[3], newProductData[4],
            newProductData[5])

        # Update the list.
        self.updateList(None)

        return True

    def onEditMulti(self, count=-1):
        """
        """

        # Get the selected item index from the list.
        productIndex = self.productList.GetFirstSelected()

        # Get the string value of the old product.
        product = self.productList.GetItemText(productIndex)

        # Extract the attributes from the database.
        oldProductData = iface.getProduct(product)

        # Create the custom text entry dialog box.
        editDialog = InputDialog(self, title="Edit Products", size=(300, 275))

        # Set the first two fields as disabled.
        editDialog.textInputs[0].Disable()
        editDialog.textInputs[1].Disable()

        # Set the first editable text control input to have its text selected.
        editDialog.textInputs[2].SelectAll()
        editDialog.textInputs[2].SetFocus()

        # If OK is pressed get the data, otherwise return false.
        if editDialog.ShowModal() == wx.ID_OK:
            newProductData = editDialog.getTextEntry()
        else:
            return False

        # Destroy the dialog box.
        editDialog.Destroy()

        # If the number of selected items was not inputted, find it.
        if count == -1:
            count = self.productList.GetSelectedItemCount()

        # Get the first selected product index from the list.
        productIndex = self.productList.GetFirstSelected()

        # Iterate through the selected products, removing old and adding new
        # data.
        for i in range(0, count):
            # Get the product text.
            product = self.productList.GetItemText(productIndex)

            # Get the data for that product.
            productData = iface.getProduct(product)

            # Only change the last four elements to the new data if an empty
            # string was not input.
            for j in range(2, 6):
                if newProductData[j] != "":
                    productData[j] = newProductData[j]

            # Remove the altered product from the databse.
            iface.removeProduct(product)

            # Add the inputted product data to the database.
            iface.addProduct(productData[0], productData[1], productData[2],
                productData[3], productData[4], productData[5])

            # Get the next selected item index.
            productIndex = self.productList.GetNextSelected(productIndex)

        # Update the list.
        self.updateList(None)

        return True

    def onDelete(self, event):
        """
        """

        # Get the first selected product index from the list.
        productIndex = self.productList.GetFirstSelected()

        # Send an error if nothing is selected.
        if productIndex == -1:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK | wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Remove all selected items.
        for i in range(0, self.productList.GetSelectedItemCount()):
            # Get the product text.
            product = self.productList.GetItemText(productIndex)

            # Remove the selected item.
            iface.removeProduct(product)

            # Get the next selected item index.
            productIndex = self.productList.GetNextSelected(productIndex)

        # Update the list.
        self.updateList(None)

        return True

    def onReport(self, event):
        """
        """

        pass

    def onOpen(self, event):
        """
        """

        self.Close()

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

class InputDialog(wx.Dialog):
    """
    To Do:
      Change the hierarchy inputs to combo boxes instead of text controls.
    """

    def __init__(self, *args, **kwargs):
        """
        """

        super(InputDialog, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        """
        """

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the content sizer.
        contentSizer = wx.FlexGridSizer(6, 2, 5, 10)

        # Create the text control inputs.
        labels = ["Product", "Sku", "Account", "Class", "Category",
            "Subcategory"]
        self.textInputs = []
        for i in range(0, 6):
            self.textInputs.append(wx.TextCtrl(masterPanel, size=(150, -1)))

            # Add the labels and text control inputs to the content sizer.
            contentSizer.AddMany([wx.StaticText(masterPanel, label=labels[i]),
                self.textInputs[i]])

        # Create the button sizer.
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the OK button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the button sizer.
        buttonSizer.AddMany([okButton, (5, 0), cancelButton, (5, 0)])

        # Bind the button presses to functions.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        # Add everything to the master sizer.
        masterSizer.Add((0, 5))
        masterSizer.Add(contentSizer, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(280, 20)),
            flag=wx.ALIGN_CENTER)
        masterSizer.Add(buttonSizer, flag=wx.ALIGN_RIGHT)
        masterSizer.Add((0, 5))

        # Set the master sizer.
        masterPanel.SetSizer(masterSizer)

    def getTextEntry(self):
        """
        """

        # Initialize the returned inputs list.
        inputs = []

        # Iterate over the text control inputs and get their value.
        for textInput in self.textInputs:
            inputs.append(textInput.GetValue())

        return inputs

    def setTextEntry(self, text):
        """
        """

        # Declare an error if the length of the input is not six.
        if len(text) != 6:
            print("setTextEntry: Error: The input must be a list of strings" +
                " with a length 6.")
            return False

        # Iterate over the text control inputs and set their value.
        i = 0
        for textInput in self.textInputs:
            textInput.SetValue(text[i])
            i += 1

        # Set the first text control input to have its text selected.
        self.textInputs[0].SelectAll()

        return True

    def onOK(self, event):
        """
        """

        self.EndModal(wx.ID_OK)

    def onCancel(self, event):
        """
        """

        self.EndModal(wx.ID_CANCEL)

""" Start Application """
def main():
    """
    """

    app = wx.App()
    ManagerFrame(None)#, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
