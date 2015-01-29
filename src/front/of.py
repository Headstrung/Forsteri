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
import csv
import interface as iface
import wx

""" Frame Class """
class ManagerFrame(wx.Frame):
    """
    To Do:
      1) Add a mass add function through a button/menu or something.
      2) Bind the closing by X to the onClose function without breaking.

    To Do Far:
      1) Add ways to search for products. Being by chemical or component.
      2) Make the header clickable and sort by that column when clicked.
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
        self.productList = wx.ListCtrl(masterPanel, size=(700, 400),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.productList.InsertColumn(0, "Product", width=136)
        self.productList.InsertColumn(1, "Account", width=136)
        self.productList.InsertColumn(2, "Class", width=136)
        self.productList.InsertColumn(3, "Category", width=136)
        self.productList.InsertColumn(4, "Subcategory", width=136)

        # Bind the selection of an item to a function.
        self.productList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)
        self.productList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelected)

        """Initialize the manipulate buttons."""
        # Create the manipulate sizer.
        manipSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        self.addButton = wx.Button(masterPanel, id=wx.ID_ADD)
        self.editButton = wx.Button(masterPanel, id=wx.ID_EDIT)
        self.deleteButton = wx.Button(masterPanel, id=wx.ID_DELETE)

        # Add the buttons to the manipulate sizer.
        manipSizer.AddMany([self.addButton, (5, 0), self.editButton, (5, 0),
            self.deleteButton])

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)

        # Bind button presses to functions.
        self.addButton.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOverAdd)
        self.addButton.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseOffAdd)
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.editButton.Bind(wx.EVT_BUTTON, self.onEdit)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

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
        selectSizer.Add(wx.StaticLine(masterPanel, size=(700, 20)),
            flag=wx.ALIGN_CENTER)
        selectSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT)
        selectSizer.AddSpacer(5)

        # Add everything to the master sizer.
        masterSizer.Add((5, 0))
        masterSizer.Add(searchSizer, flag=wx.ALIGN_TOP|wx.EXPAND)
        masterSizer.Add(selectSizer, flag=wx.EXPAND)

        # Update the displayed list.
        self.updateList(None)

        # Set the sizer for the main panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((875, 532))
        self.SetTitle("Open/Manage Products")
        self.Centre()
        self.Show(True)

    """ Helper Functions """
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
          1) Check which implementation is faster between match and product.
          2) Implement the search functionality (possibly in another function).
        """

        """Get match implementation."""

        # Get the lists of data from the database.
        data = [iface.getMatch("product")]
        for label in self.labelStrings:
            data.append(iface.getMatch(label))

        # Reset the color of the edit and delete buttons.
        self.editButton.SetBackgroundColour(wx.NullColour)
        self.deleteButton.SetBackgroundColour(wx.NullColour)

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

    def readAddData(self, path):
        """
        """

        # Open the file and save it in the data variable.
        data = []
        newProducts = []
        with open(path, newline='') as csvFile:
            reader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in reader:
                # Find the length of the row.
                rowLength = len(row)

                # If the row is shorter than 6, pad the end with empty strings.
                if rowLength < 6:
                    for i in range(rowLength, 6):
                        row.append("")

                # Append the data and product list with the input data.
                data.append(row)
                newProducts.append(row[0])

        return data, newProducts

    """ Event Handler Functions """
    def onSelected(self, event):
        """
        """

        # If multiple products are selected, set the edit and delete buttons
        # to be yellow.
        if self.productList.GetSelectedItemCount() > 1:
            self.editButton.SetBackgroundColour("Yellow")
            self.deleteButton.SetBackgroundColour("Yellow")
        # If only one product is selected, set the edit and delete buttons
        # to be the default color.
        else:
            self.editButton.SetBackgroundColour(wx.NullColour)
            self.deleteButton.SetBackgroundColour(wx.NullColour)

        return True

    def onMouseOverAdd(self, event):
        """
        """

        # Start the timer.
        self.timer.Start(1500)

        # Continue processing events.
        event.Skip()

        return True

    def onMouseOffAdd(self, event):
        """
        """

        # Stop the timer.
        self.timer.Stop()

        # Reset the color of the add button.
        self.addButton.SetBackgroundColour(wx.NullColour)

        # Continue processing events.
        event.Skip()

        return True

    def onTimer(self, event):
        """
        """

        # Change the color of the add button.
        self.addButton.SetBackgroundColour("Yellow")

        return True

    def onAdd(self, event):
        """
        """

        # Stop the timer.
        self.timer.Stop()

        # If the add button is yellow, pass to the multi function.
        if self.addButton.GetBackgroundColour() == "Yellow":
            # Reset the color of the add button.
            self.addButton.SetBackgroundColour(wx.NullColour)

            # Call the multi add function.
            self.onAddMulti()

            return False

        # Create the custom text entry dialog box.
        addDialog = InputDialog(self, title="Add Product", size=(300, 275))

        # If OK is not pressed, return false.
        if addDialog.ShowModal() != wx.ID_OK:
            return False

        # Get the text from the dialog box.
        addProductData = addDialog.getTextEntry()

        # If an empty string is input for product send an error.
        if addProductData[0] == "":
            errorDialog = wx.MessageDialog(self,
                "Product cannot be empty.", "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
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

    def onAddMulti(self, overwrite=False):
        """
        """

        # Create the open file dialog box.
        openFileDialog = wx.FileDialog(self, "Select a mass add file.", "", "",
            "CSV files (*.csv)|*.csv|TXT files (*txt)|*.txt|XLSX and XLS " +
            "files (*.xlsx, *.xls)|*.xslx*.xls",
            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)

        # If open is not pressed return false.
        if openFileDialog.ShowModal() != wx.ID_OK:
            return False

        # Read the data from the file.
        (data, newProducts) = self.readAddData(openFileDialog.GetPath())

        # Destroy the dialog box
        openFileDialog.Destroy()

        # Create the progress dialog box.
        progressDialog = wx.ProgressDialog("Adding Products",
            "Processing products, please wait.", maximum=100, parent=self,
            style=wx.PD_CAN_ABORT|wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME
            |wx.PD_REMAINING_TIME|wx.PD_SMOOTH)

        # Initialize aspects of the progress dialog box.
        keepGoing = True
        progress = 0

        # Extract the current list of products.
        oldProducts = iface.getMatch("product")

        # Check if any overlaps occur between the old and new data.
        repeats = set(newProducts).intersection(oldProducts)

        # Update the dialog box.
        progress = 5
        (keepGoing, skip) = progressDialog.Update(progress, "Repeats found.")

        # If overwriting, remove old and add new data to the database.
        delta = 5 / (len(repeats) + 1)
        if overwrite:
            for product in repeats:
                # Find the index of the product in the new products list.
                index = newProducts.index(product)

                # Remove the altered product data from the databse.
                iface.removeProduct(product)

                # Add the inputted product data to the databse.
                iface.addProduct(data[index][0], data[index][1],
                    data[index][2], data[index][3], data[index][4],
                    data[index][5])

                # Remove the already added data from the held data.
                del data[index]
                del newProducts[index]

                # Update the dialog box.
                progress += delta
                (keepGoing, skip) = progressDialog.Update(progress,
                    product + "repeat overwritten.")
        # If not overwriting, just remove the repeated data from the held data.
        else:
            for product in repeats:
                # Find the index of the product in the new products list.
                index = newProducts.index(product)

                # Remove the repeated data from the held data.
                del data[index]
                del newProducts[index]

                # Update the dialog box.
                progress += delta
                (keepGoing, skip) = progressDialog.Update(progress,
                    product + "repeat handled.")

        # Add any remaining nonrepeated data to the database.
        index = 0
        delta = 90 / len(newProducts)
        for product in newProducts:
            iface.addProduct(data[index][0], data[index][1], data[index][2],
                data[index][3], data[index][4], data[index][5])

            # Update the dialog box.
            progress += delta
            (keepGoing, skip) = progressDialog.Update(progress,
                "Finished adding " + product + ".")

            index += 1

        # Final update to the dialog box.
        (keepGoing, skip) = progressDialog.Update(100, "Add complete.")

        # Destroy the dialog box.
        progressDialog.Destroy()

        # Update the list.
        self.updateList(None)

        return True

    def onEdit(self, event):
        """
        """

        # Check if multiple items are selected.
        count = self.productList.GetSelectedItemCount()

        # If more than one item is selected, pass to the multi function.
        if count > 1:
            # Call the multi edit function.
            self.onEditMulti(count)

            return False
        # If nothing is selected, send an error.
        elif count == 0:
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

        # If OK is not pressed, return false.
        if editDialog.ShowModal() != wx.ID_OK:
            return False

        # Get the text from the dialog box.
        newProductData = editDialog.getTextEntry()

        # If an empty string is input for product send an error.
        if newProductData[0] == "":
            errorDialog = wx.MessageDialog(self,
                "Product cannot be empty.", "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Destroy the dialog box.
        editDialog.Destroy()

        # Remove the altered product data from the databse.
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

        # Change the edit dialog for multiple edits.
        editDialog.setMultiEdit()

        # If OK is not pressed, return false.
        if editDialog.ShowModal() != wx.ID_OK:
            return False

        # Get the text from the dialog box.
        newProductData = editDialog.getTextEntry()

        # Destroy the dialog box.
        editDialog.Destroy()

        # Reset the color of the edit and delete buttons.
        self.editButton.SetBackgroundColour(wx.NullColour)
        self.deleteButton.SetBackgroundColour(wx.NullColour)

        # Create the progress dialog box.
        progressDialog = wx.ProgressDialog("Editing Products",
            "Processing products, please wait.", maximum=100, parent=self,
            style=wx.PD_CAN_ABORT|wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME
            |wx.PD_REMAINING_TIME|wx.PD_SMOOTH)

        # Initialize aspects of the progress dialog box.
        keepGoing = True
        progress = 0

        # If the number of selected items was not inputted, find it.
        if count == -1:
            count = self.productList.GetSelectedItemCount()

        # Get the first selected product index from the list.
        productIndex = self.productList.GetFirstSelected()

        # Iterate through the selected products, removing old and adding new
        # data.
        delta = 99 / count
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

            # Update the dialog box.
            progress += delta
            progressDialog.Update(progress, "Finished editing " + product +
                ".")

        # Final update to the dialog box.
        (keepGoing, skip) = progressDialog.Update(100, "Edit complete.")

        # Destroy the dialog box.
        progressDialog.Destroy()

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
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()
            return False

        # Get the number of selected products.
        count = self.productList.GetSelectedItemCount()

        # Create the confimation dialog box.
        confirmDialog = wx.MessageDialog(self,
            "You are about to delete " + str(count) +
            " product(s). Continue?",
            "Delete Confirmation", wx.YES_NO)

        # If no is selected, return false.
        if confirmDialog.ShowModal() != wx.ID_YES:
            return False

        # Destroy the dialog box.
        confirmDialog.Destroy()

        # Reset the color of the edit and delete buttons.
        self.editButton.SetBackgroundColour(wx.NullColour)
        self.deleteButton.SetBackgroundColour(wx.NullColour)

        # Create the progress dialog box.
        progressDialog = wx.ProgressDialog("Deleting Products",
            "Processing products, please wait.", maximum=100, parent=self,
            style=wx.PD_CAN_ABORT|wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME
            |wx.PD_REMAINING_TIME|wx.PD_SMOOTH)

        # Initialize aspects of the progress dialog box.
        keepGoing = True
        progress = 0

        # Remove all selected items.
        delta = 100 / count
        for i in range(0, count):
            # Get the product text.
            product = self.productList.GetItemText(productIndex)

            # Remove the selected item.
            iface.removeProduct(product)

            # Get the next selected item index.
            productIndex = self.productList.GetNextSelected(productIndex)

            # Update the dialog box.
            progress += delta
            progressDialog.Update(progress, "Finished deleting " + product +
                ".")

        # Final update to the dialog box.
        (keepGoing, skip) = progressDialog.Update(100, "Delete complete.")

        # Destroy the dialog box.
        progressDialog.Destroy()

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

        # Close the frame.
        self.Close()

        return True

    def onOK(self, event):
        """
        """

        # Remove the unaltered version of the database file.
        iface.removeDB()

        # Close the frame.
        self.Close()

        return True

    def onCancel(self, event):
        """
        """

        # Replace the database file with the unaltered version.
        iface.replaceDB()

        # Close the frame.
        self.Close()

        return True

class InputDialog(wx.Dialog):
    """
    To Do:
      1) Change the hierarchy inputs to combo boxes instead of text controls.
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

    def setMultiEdit(self):
        """
        """

        # Set the first two fields as disabled.
        self.textInputs[0].Disable()
        self.textInputs[1].Disable()

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
