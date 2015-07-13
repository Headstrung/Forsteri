"""
Open/Manage Products Dialog

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
import csv
import datetime as dt
import os
import pickle
import sqlite3
import wx

# Import forsteri modules.
from forsteri.interface import data as idata
from forsteri.interface import sql as isql

# Create global labels.
LABELS = ["product", "sku", "account", "class", "category", "subcategory"]

class OpenDialog(wx.Dialog):
    """
    A dialog containing all products that are contained within the master
    database. Also, a sorting feature based on the product's description is
    included. From this dialog products can be altered, added, and removed.
    This is the location where reports will be generated and products will be
    opened.

    Extends:
      wx.Dialog

    To Do:
      1) Make the updating of list items occur without removing all items and
        adding new back.
      2) Add ways to search for products. Being by chemical or component.
      3) Make the header clickable and sort by that column when clicked.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the open products dialog.

        Args:
          *args (tuple of object): Any arguments to be passed directly to the
            super's constructor.
          **kwargs (dictionary of name: object): Any keyword arguments to be
            passed to the super's constructor.

        Returns:
          OpenDialog
        """

        ## Frame
        # Initialize by the parent's constructor.
        super(OpenDialog, self).__init__(*args, **kwargs)

        # Create the sieve.
        self.sieve = dict.fromkeys(LABELS)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Search By
        # Create the search by static box.
        searchSB = wx.StaticBox(masterPanel, label="Search by")

        # Create the search sizer.
        searchSizer = wx.StaticBoxSizer(searchSB, wx.VERTICAL)

        # Create the name type sizer.
        nameSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the name type radio buttons.
        self.productRB = wx.RadioButton(masterPanel, label="Product",
            style=wx.RB_GROUP)
        skuRB = wx.RadioButton(masterPanel, label="Sku")

        # Add the name type radio buttons to the name type sizer.
        nameSizer.AddMany([(5, 0), self.productRB, (25, 0), skuRB, (5, 0)])

        # Bind the radio buttons to a function.
        self.productRB.Bind(wx.EVT_RADIOBUTTON, self.updateList)
        skuRB.Bind(wx.EVT_RADIOBUTTON, self.updateList)

        # Get the label strings and combo box choices.
        choices = self.getChoices()

        # Create the text labels and input boxes.
        textLabels = [None] * 4
        self.inputs = [None] * 5

        # Create the text entry for the name.
        self.inputs[0] = wx.TextCtrl(masterPanel, size=(150, -1))

        # Add the name type and text entry to the search sizer.
        searchSizer.AddMany([(0, 10), nameSizer, (0, 5)])
        searchSizer.Add(self.inputs[0], flag=wx.LEFT|wx.RIGHT, border=5)

        # Bind text entry to a function.
        self.inputs[0].Bind(wx.EVT_TEXT, self.updateList)

        # Create subsequent label and combo boxes, add them to the search
        # sizer, and bind them to functions.
        for i in range(0, 3):
            textLabels[i] = wx.StaticText(masterPanel,
                label=LABELS[i + 2].title())
            self.inputs[i + 1] = wx.ComboBox(masterPanel, size=(150, -1),
                choices=choices[i], style=wx.CB_READONLY|wx.CB_SORT)
            searchSizer.AddSpacer(10)
            searchSizer.Add(textLabels[i], flag=wx.LEFT|wx.BOTTOM, border=5)
            searchSizer.Add(self.inputs[i + 1], flag=wx.LEFT|wx.RIGHT,
                border=5)
            self.inputs[i + 1].Bind(wx.EVT_COMBOBOX, self.updateList)

        ## Selection
        # Create the selection sizer.
        selectSizer = wx.BoxSizer(wx.VERTICAL)

        ## List Control
        # Create the list control.
        self.productList = wx.ListCtrl(masterPanel, size=(710, 400),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.productList.InsertColumn(0, "Product", width=136)
        self.productList.InsertColumn(1, "Account", width=136)
        self.productList.InsertColumn(2, "Class", width=136)
        self.productList.InsertColumn(3, "Category", width=136)
        #self.productList.InsertColumn(4, "Subcategory", width=136)

        # Bind the selection of an item to a function.
        self.productList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelected)
        self.productList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelected)
        self.productList.Bind(wx.EVT_LEFT_DCLICK, self.onOpen)

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

        # Create a timer for edit.
        self.timer = wx.Timer(self)

        # Bind the timer to a function.
        self.Bind(wx.EVT_TIMER, self.onTimer)

        # Bind button presses to functions.
        self.addButton.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOverAdd)
        self.addButton.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseOffAdd)
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.editButton.Bind(wx.EVT_BUTTON, self.onEdit)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

        # Add tool tips to the buttons.
        self.addButton.SetToolTipString("Add a product to the database. " +\
            "Hover over to switch to multi-add mode.")
        self.editButton.SetToolTipString("Edit the selected product(s).")
        self.deleteButton.SetToolTipString("Delete the selected product(s).")

        ## Finish Buttons
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        reportButton = wx.Button(masterPanel, label="&Report")
        openButton = wx.Button(masterPanel, id=wx.ID_OPEN)
        applyButton = wx.Button(masterPanel, id=wx.ID_APPLY)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the ok button to be the dafault button.
        openButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([reportButton, (5, 0), openButton, (5, 0),
            applyButton, (5, 0), cancelButton, (5, 0)])

        # Bind the button presses to function.
        reportButton.Bind(wx.EVT_BUTTON, self.onReport)
        openButton.Bind(wx.EVT_BUTTON, self.onOpen)
        applyButton.Bind(wx.EVT_BUTTON, self.onApply)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        # Add tool tips to the buttons.
        reportButton.SetToolTipString("Generate a forecast report for the " +\
            "selected product(s).")
        openButton.SetToolTipString("Open the selected product.")
        applyButton.SetToolTipString("Record any changes to products.")
        cancelButton.SetToolTipString("Cancel any changes to products and " +\
            "close.")

        ## Key Bindings
        # Create a new id for selecting all.
        selectAllId = wx.NewId()

        # Bind the id to a function.
        self.Bind(wx.EVT_MENU, self.selectAll, id=selectAllId)

        # Create a new accelerator table and set it to the frame.
        accelT = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord("A"), selectAllId)])
        self.SetAcceleratorTable(accelT)

        # Add the items to the selection sizer.
        selectSizer.Add(self.productList,
            flag=wx.LEFT|wx.RIGHT|wx.TOP, border=5)
        selectSizer.AddSpacer(10)
        selectSizer.Add(manipSizer, flag=wx.ALIGN_CENTER)
        selectSizer.AddSpacer(9)
        selectSizer.Add(wx.StaticLine(masterPanel, size=(710, 2)),
            flag=wx.ALIGN_CENTER)
        selectSizer.AddSpacer(9)
        selectSizer.Add(finishSizer, flag=wx.ALIGN_RIGHT)
        selectSizer.AddSpacer(5)

        ## Frame Operations
        # Add everything to the master sizer.
        masterSizer.Add(searchSizer,
            flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_TOP|wx.EXPAND, border=5)
        masterSizer.Add(selectSizer, flag=wx.EXPAND)

        # Open a connection to the database.
        self.connection = sqlite3.connect(isql.MASTER)

        # Update the displayed list.
        self.updateList(None)

        # Set the sizer for the main panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((900-136, 528))
        self.Centre()

    """
    Manipulate Functions
    """
    def getSelection(self):
        """
        """

        # Get the first selected index.
        productIndex = self.productList.GetFirstSelected()

        # Determine how many products are selected.
        count = self.productList.GetSelectedItemCount()

        # Create a list of products.
        selected = []

        # Iterate over all selected products.
        index = 1
        while index <= count:
            # Add the next product to the list of products.
            selected.append(self.productList.GetItemText(productIndex))

            # Find the next selected index.
            productIndex = self.productList.GetNextSelected(productIndex)

            # Increment the index.
            index += 1

        return selected

    """
    Helper Functions
    """
    def getChoices(self):
        """
        Pull the possible choices for the combo boxes from the database.

        Args:
          None

        Returns:
          list of list of str: The lists of choices for each combo box in the
            dialog box.
        """

        # Get the list of tiers.
        tiers = isql.getTiers()

        # Get each list associated with each tier.
        connect = []
        for tier in tiers:
            tierList = isql.getForTier(tier)

            # Add an empty string for selection.
            tierList.append("")

            # Append the entire list to the returned list.
            connect.append(tierList)

        # Switch the indices of category and class.
        connect[1], connect[2] = connect[2], connect[1]

        return connect

    def readAddData(self, path):
        """
        """

        # Open the file and save it in the data variable.
        newData = []
        newProducts = []
        with open(path) as csvFile:
            reader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in reader:
                # Find the length of the row.
                rowLength = len(row)

                # If the row is shorter than 6, pad the end with empty strings.
                if rowLength < 6:
                    for i in range(rowLength, 6):
                        row.append("")

                # Append the data and product list with the input data.
                newData.append({"product": row[0], "sku": row[1],
                    "account": row[2], "class": row[3], "category": row[4],
                    "subcategory": row[5]})
                newProducts.append(row[0])

        return newData, newProducts

    def siftForecast(self, forecast):
        """
        """

        final = []
        today = dt.date(1, 1, 1).today()

        for i in range(1, 13):
            if i > today.month:
                year = today.year
            else:
                year = today.year + 1
            try:
                final.append(round(forecast[dt.datetime(year, i, 1)]))
            except KeyError:
                final.append("")

        return final

    """
    Event Handler Functions
    """
    def updateList(self, event):
        """
        To Do:
          1) Get the scroll bar to not change location when updating.
        """

        # Get the search criterion.
        if self.productRB.GetValue():
            self.sieve["product"] = self.inputs[0].GetValue()
            self.sieve["sku"] = ''
        else:
            self.sieve["product"] = ''
            self.sieve["sku"] = self.inputs[0].GetValue()
        self.sieve["account"] = self.inputs[1].GetStringSelection()
        self.sieve["class"] = self.inputs[2].GetStringSelection()
        self.sieve["category"] = self.inputs[3].GetStringSelection()
        #self.sieve["subcategory"] = self.inputs[4].GetStringSelection()

        # Get all of the products from the database.
        data = isql.getData(self.sieve, self.connection)

        # Set the title of the frame.
        self.SetTitle("Open/Manage: " + str(len(data)) + " Products")

        # Reset the color of the edit and delete buttons.
        self.editButton.SetBackgroundColour(wx.NullColour)
        self.deleteButton.SetBackgroundColour(wx.NullColour)

        # Remove all items from the list control and reset the index.
        self.productList.DeleteAllItems()
        index = 0

        # Add the items to the list control.
        for product in data:
            self.productList.InsertStringItem(index, product[0])
            self.productList.SetStringItem(index, 1, product[2])
            self.productList.SetStringItem(index, 2, product[3])
            self.productList.SetStringItem(index, 3, product[4])
            #self.productList.SetStringItem(index, 4, product[5])
            index += 1

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

    def selectAll(self, event):
        """
        """

        # Iterate through the items in the list selecting each.
        for i in range(0, self.productList.GetItemCount()):
            self.productList.Select(i)

    def onMouseOverAdd(self, event):
        """
        """

        # Start the timer.
        self.timer.Start(1500)

        # Continue processing events.
        event.Skip()

    def onMouseOffAdd(self, event):
        """
        """

        # Stop the timer.
        self.timer.Stop()

        # Reset the color of the add button.
        self.addButton.SetBackgroundColour(wx.NullColour)

        # Continue processing events.
        event.Skip()

    def onTimer(self, event):
        """
        """

        # Change the color of the add button.
        self.addButton.SetBackgroundColour("Yellow")

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
            self.onAddMulti(event)

            return

        # Create the custom text entry dialog box.
        addDialog = InputDialog(self, title="Add Product")

        # If OK is not pressed, return false.
        if addDialog.ShowModal() != wx.ID_OK:
            return

        # Get the text from the dialog box.
        addProductData = addDialog.getTextEntry(missing=False)

        # Do nothing if the length of the inputted data is zero.
        if len(addProductData) == 0:
            return

        # If nothing is input for product send an error and return false.
        if "product" not in addProductData.keys():
            errorDialog = wx.MessageDialog(self,
                "Product cannot be empty.", "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Destroy the dialog box.
        addDialog.Destroy()

        # Add the inputted product data to the database.
        isql.addProduct(addProductData, self.connection)

        # Update the list.
        self.updateList(None)

    def onAddMulti(self, event, overwrite=True):
        """
        """

        # Create the open file dialog box.
        openFileDialog = wx.FileDialog(self, "Select a Mass Add File", "", "",
            "CSV files (*.csv)|*.csv|TXT files (*txt)|*.txt|XLSX and XLS " +
            "files (*.xlsx, *.xls)|*.xslx*.xls",
            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)

        # If open is not pressed, return false.
        if openFileDialog.ShowModal() != wx.ID_OK:
            return

        # Read the data from the file.
        (data, newProducts) = self.readAddData(openFileDialog.GetPath())

        # Destroy the dialog box
        openFileDialog.Destroy()

        # Add the products to the database.
        isql.addProducts(newProducts, data, overwrite, self.connection)

        # Update the list.
        self.updateList(None)

    def onEdit(self, event):
        """
        """

        # Check if multiple items are selected.
        count = self.productList.GetSelectedItemCount()

        # If more than one item is selected, pass to the multi function.
        if count > 1:
            # Call the multi edit function.
            self.onEditMulti(event, count)

            return
        # If nothing is selected, send an error.
        elif count == 0:
            errorDialog = wx.MessageDialog(self, "No item was selected.",
                "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Get the selected item index from the list.
        productIndex = self.productList.GetFirstSelected()

        # Get the string value of the old product.
        product = self.productList.GetItemText(productIndex)

        # Extract the attributes from the database.
        oldProductData = isql.getProduct(product, self.connection)

        # Create the custom text entry dialog box.
        editDialog = InputDialog(self, title="Edit Product")

        # Set the initial text to be the old product.
        editDialog.setTextEntry(oldProductData)

        # If OK is not pressed, return false.
        if editDialog.ShowModal() != wx.ID_OK:
            return

        # Get the text from the dialog box.
        newProductData = editDialog.getTextEntry(missing=True)

        # If nothing is input for product send an error and return false.
        if newProductData["product"] == '':
            errorDialog = wx.MessageDialog(self,
                "Product cannot be empty.", "Error", wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Destroy the dialog box.
        editDialog.Destroy()

        # Iterate over the inputs and delete unchanged values.
        for index in range(0, len(newProductData)):
            if newProductData[LABELS[index]] == oldProductData[index]:
                del newProductData[LABELS[index]]

        # Do nothing if the length of the inputted data is zero.
        if len(newProductData) == 0:
            return

        # Add the inputted product data to the database.
        isql.setProduct(oldProductData[0], newProductData, self.connection)

        # Update the list.
        self.updateList(None)

    def onEditMulti(self, event, count=None):
        """
        """

        # Create the custom text entry dialog box.
        editDialog = InputDialog(self, title="Edit Products")

        # Change the edit dialog for multiple edits.
        editDialog.setMultiEdit()

        # If OK is not pressed, return false.
        if editDialog.ShowModal() != wx.ID_OK:
            return

        # Get the text from the dialog box.
        newProductData = editDialog.getTextEntry()

        # Destroy the dialog box.
        editDialog.Destroy()

        # Reset the color of the edit and delete buttons.
        self.editButton.SetBackgroundColour(wx.NullColour)
        self.deleteButton.SetBackgroundColour(wx.NullColour)

        # If the number of selected items was not inputted, find it.
        if count is None:
            count = self.productList.GetSelectedItemCount()

        # Get the list of products that have been selected.
        products = []
        productIndex = self.productList.GetFirstSelected()
        for index in range(0, count):
            products.append(self.productList.GetItemText(productIndex))
            productIndex = self.productList.GetNextSelected(productIndex)

        # Update the values input in the database.
        isql.setProducts(products, newProductData, self.connection)

        # Update the list.
        self.updateList(None)

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
            return

        # Get the number of selected products.
        count = self.productList.GetSelectedItemCount()

        # Create the confimation dialog box.
        confirmDialog = wx.MessageDialog(self,
            "You are about to delete " + str(count) +
            " product(s). Continue?",
            "Delete Confirmation", wx.YES_NO)

        # If no is selected, return false.
        if confirmDialog.ShowModal() != wx.ID_YES:
            return

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
        delta = 99 / count
        index = 1
        while keepGoing and index <= count:
            # Get the product text.
            product = self.productList.GetItemText(productIndex)

            # Remove the selected item.
            isql.removeProduct(product, self.connection)

            # Get the next selected item index.
            productIndex = self.productList.GetNextSelected(productIndex)

            # Update the dialog box.
            progress += delta
            (keepGoing, skip) = progressDialog.Update(progress,
                "Finished deleting " + product + ".")

            # Increment the index.
            index += 1

        # Final update to the dialog box.
        (keepGoing, skip) = progressDialog.Update(100, "Delete complete.")

        # Destroy the dialog box.
        progressDialog.Destroy()

        # Update the list.
        self.updateList(None)

    def onReport(self, event):
        """
        """

        # Get the list of selected items.
        products = self.getSelection()

        # Get the preferences for reporting.
        pref = pickle.load(open(os.path.join(idata.DATA, "Forsteri",
            "pref.p"), "rb"))

        # Get the method type.
        method = pref["report_type"].lower()
        if method == "auto":
            method = None

        # Open a connection to the data database.
        dataConnection = sqlite3.connect(idata.MASTER)

        # Iterate over the products selected.
        data = {}
        for product in products:
            data[product] = idata.getForecast(product, method,
                connection=dataConnection)

        # Create the file dialog box.
        fileDialog = wx.FileDialog(self, "Save file as", "", "",
            "CSV files (*.csv)|*.csv", wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        # Show the file dialog box.
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return

        # Get the location of the save.
        loc = fileDialog.GetPath()

        # Write the data to a file.
        with open(loc, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|')
            writer.writerow(["Product", "January", "February", "March",
                "April", "May", "June", "July", "August", "September",
                "October", "November", "December"])
            for product in products:
                temp = [product]
                temp.extend(self.siftForecast(data[product]))
                writer.writerow(temp)

        # Close the database connections.
        self.connection.close()
        dataConnection.close()

        # End the modal and return the print id.
        self.EndModal(wx.ID_PRINT)

    def onOpen(self, event):
        """
        """

        # Commit the changes to the database.
        self.connection.commit()

        # Close the database.
        self.connection.close()

        # End the modal and return the ok id.
        self.EndModal(wx.ID_OPEN)

    def onApply(self, event):
        """
        """

        # Commit the changes to the database.
        self.connection.commit()

    def onCancel(self, event):
        """
        """

        # Close the database.
        self.connection.close()

        # End the modal and return the cancel id.
        self.EndModal(wx.ID_CANCEL)

"""
Input Dialog Box Class
"""
class InputDialog(wx.Dialog):
    """
    A dialog containing the input boxes for an item. This dialog is used for
    adding and editing a single item and can be used to edit multiple items.

    Extends:
      wx.Dialog
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the input dialog.

        Args:
          *args (tuple of object): Any arguments to be passed directly to the
            super's constructor.
          **kwargs (dictionary of name: object): Any keyword arguments to be
            passed to the super's constructor.

        Returns:
          InputDialog
        """

        # Initialize by the parent's constructor.
        super(InputDialog, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the content sizer.
        contentSizer = wx.FlexGridSizer(6, 2, 5, 10)

        # Get the choices for the combo boxes.
        choices = self.pullChoices()

        # Create the text control and combo box inputs.
        self.inputObjects = []
        for i in range(0, 5):
            if i < 2:
                self.inputObjects.append(wx.TextCtrl(masterPanel,
                    size=(150, -1)))
            else:
                self.inputObjects.append(wx.ComboBox(masterPanel,
                    size=(150, -1), choices=choices[i - 2],
                    style=wx.CB_READONLY|wx.CB_SORT))

            # Add the labels and text control inputs to the content sizer.
            contentSizer.AddMany([wx.StaticText(masterPanel,
                label=LABELS[i].title()), self.inputObjects[i]])

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
        masterSizer.AddSpacer(9)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(280, 2)),
            flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(9)
        masterSizer.Add(buttonSizer, flag=wx.ALIGN_RIGHT)
        masterSizer.Add((0, 5))

        # Set the master sizer.
        masterPanel.SetSizer(masterSizer)

        # Set the size of the window.
        self.SetSize((300, 233))

    """
    Manipulate Functions
    """
    def getTextEntry(self, missing=True):
        """
        Get the inputted values from the dialog box.

        Args:
          missing (bool, optional): True if the missing inputs are to be
            preserved as None, otherwise false.

        Retruns:
          dict of {str: str}: The inputted values in the form attribute: value.
        """

        # Initialize the returned inputs dictionary.
        inputs = dict()

        # Iterate over the input objects.
        index = 0
        for inputObject in self.inputObjects:
            # Get the input value.
            entered = inputObject.GetValue()

            # If the missing flag is false and the entered value is an empty
            # string, increment the index and move to the next loop iteration.
            if not missing and entered == '':
                # Increment the index and skip to the next loop iteration.
                index += 1
                continue

            # Set the correct label to the inputted value.
            inputs[LABELS[index]] = entered

            # Increment the index.
            index += 1

        return inputs

    def setTextEntry(self, text):
        """
        Set the values in input dialog box.

        Args:
          text (list of str): A list containing the values to be input into the
            entry fields.

        Returns:
          bool: True if successful, false otherwise.
        """

        # Iterate over the text control inputs and set their value.
        index = 0
        for inputObject in self.inputObjects:
            inputObject.SetValue(text[index])
            index += 1

        # Set the first text control input to have its text selected.
        self.inputObjects[0].SelectAll()

        return True

    def setMultiEdit(self):
        """
        Set the dialog box to be for multiple edits. This disables anything
        that is unique to a product.
        
        Args:
          None

        Returns:
          bool: True if successful, false otherwise.
        """

        # Set the first two fields as disabled.
        self.inputObjects[0].Disable()
        self.inputObjects[1].Disable()

        return True

    """
    Helper Functions
    """
    def pullChoices(self):
        """
        Pull the possible choices for the combo boxes from the database.

        Args:
          None

        Returns:
          list of list of str: The lists of choices for each combo box in the
            dialog box.
        """

        # Get the list of tiers.
        tiers = isql.getTiers()

        # Get each list associated with each tier.
        connect = []
        for tier in tiers:
            tierList = isql.getForTier(tier)

            # Add an empty string for selection.
            tierList.append("")

            # Append the entire list to the returned list.
            connect.append(tierList)

        # Switch the indices of category and class.
        connect[1], connect[2] = connect[2], connect[1]

        return connect

    """
    Event Handler Functions
    """
    def onOK(self, event):
        """
        What to do when the OK button is pressed.

        Args:
          event(wx._core.CommandEvent): The triggered event when the OK button
            is pressed.

        Returns:
          None
        """

        self.EndModal(wx.ID_OK)

    def onCancel(self, event):
        """
        What to do when the cancel button is pressed.

        Args:
          event(wx._core.CommandEvent): The triggered event when the cancel
            button is pressed.

        Returns:
          None
        """

        self.EndModal(wx.ID_CANCEL)

if __name__ == '__main__':
    app = wx.App()
    dialog = OpenDialog(None,
        style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    dialog.ShowModal()
