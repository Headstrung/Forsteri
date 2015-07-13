#!/usr/bin/python

"""
Product Panel

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
import datetime as dt
import numpy as np
import wx

# Import forsteri modules.
from forsteri.gui.window import data_viewer as dv
from forsteri.interface import data as idata
from forsteri.interface import sql as isql
from forsteri.process import model as pm

class ProductPanel(wx.Panel):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        ## Panel
        # Initialize the parents constructor.
        super(ProductPanel, self).__init__(*args, **kwargs)

        # Create the product variable.
        self.product = None

        # Create the model type variable.
        self.modelType = "mlr"

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## Product Attributes
        # Create the product attributes sizer.
        productSizer = wx.GridBagSizer(5, 5)

        ## Product Information
        # Create the product information sizer.
        infoSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the static text for each attribute.
        self.nameText = wx.StaticText(self)
        self.accountText = wx.StaticText(self)
        self.classText = wx.StaticText(self)
        self.categoryText = wx.StaticText(self)
        #self.subcategoryText = wx.StaticText(self)

        # Create the fonts for the static texts.
        titleFont = wx.Font(22, wx.SWISS, wx.NORMAL, wx.BOLD)
        infoFont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.LIGHT)

        # Set the fonts for the static texts.
        self.nameText.SetFont(titleFont)
        self.accountText.SetFont(infoFont)
        self.classText.SetFont(infoFont)
        self.categoryText.SetFont(infoFont)
        #self.subcategoryText.SetFont(infoFont)

        # Add the static text to the sizer.
        infoSizer.Add(self.nameText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.accountText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.classText, flag=wx.LEFT, border=5)
        infoSizer.Add(self.categoryText, flag=wx.LEFT, border=5)
        #infoSizer.Add(self.subcategoryText, flag=wx.LEFT, border=5)

        ## Variables
        # Create the variables static box.
        variablesSB = wx.StaticBox(self, label="Variables")

        # Create the variables sizer.
        variablesSizer = wx.StaticBoxSizer(variablesSB, wx.VERTICAL)

        # Create the list control.
        self.variablesList = wx.ListCtrl(self, size=(335, 150),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Bind actions to functions.
        self.variablesList.Bind(wx.EVT_LEFT_DCLICK, self.onVariable)

        # Add columns to the list control.
        self.variablesList.InsertColumn(0, "Variable", width=150)
        self.variablesList.InsertColumn(1, "Latest Data", width=95)
        self.variablesList.InsertColumn(2, "Count", width=65)

        # Add the list control to the sizer.
        variablesSizer.Add(self.variablesList, flag=wx.ALL, border=5)

        ## Related Items
        # Create the related items static box.
        relatedSB = wx.StaticBox(self, label="Related Items")

        # Create the related items sizer.
        relatedSizer = wx.StaticBoxSizer(relatedSB, wx.VERTICAL)

        # Create the list box.
        self.relatedList = wx.ListBox(self, size=(150, 150))

        # Bind actions to functions.
        self.relatedList.Bind(wx.EVT_LEFT_DCLICK, self.onRelated)

        # Add the list box to the sizer.
        relatedSizer.Add(self.relatedList, flag=wx.ALL, border=5)

        ## Linked Items
        # Create the related items static box.
        linkedSB = wx.StaticBox(self, label="Linked Items")

        # Create the related items sizer.
        linkedSizer = wx.StaticBoxSizer(linkedSB, wx.VERTICAL)

        # Create the list box.
        self.linkedList = wx.ListBox(self, size=(150, 150))

        # Add the list box to the sizer.
        linkedSizer.Add(self.linkedList, flag=wx.ALL, border=5)

        ## Finish Product Attributes
        # Add everything to the product sizer.
        productSizer.Add(infoSizer, pos=(0, 0), flag=wx.LEFT|wx.TOP, border=5)
        productSizer.Add(variablesSizer, pos=(0, 1), flag=wx.TOP, border=5)
        productSizer.Add(relatedSizer, pos=(0, 2), flag=wx.TOP, border=5)
        productSizer.Add(linkedSizer, pos=(0, 3),
            flag=wx.TOP|wx.RIGHT|wx.BOTTOM, border=5)

        # Make the first column growable.
        productSizer.AddGrowableCol(0)

        ## Forecast
        # Create the forecast sizer.
        forecastSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the model type sizer.
        typeSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the forecast label.
        forecastText = wx.StaticText(self, label="Forecast")

        # Set the font for the forecast text.
        forecastText.SetFont(infoFont)

        # Create the radio buttons.
        buttonOne = wx.RadioButton(self, label="MLR", style=wx.RB_GROUP)
        buttonTwo = wx.RadioButton(self, label="EMA")
        buttonThree = wx.RadioButton(self, label="Naive")

        # Bind the buttons to functions.
        buttonOne.Bind(wx.EVT_RADIOBUTTON, lambda event:
            self.onRadioButton(event, "mlr"))
        buttonTwo.Bind(wx.EVT_RADIOBUTTON, lambda event:
            self.onRadioButton(event, "ema"))
        buttonThree.Bind(wx.EVT_RADIOBUTTON, lambda event:
            self.onRadioButton(event, "naive"))

        # Add the items to the type sizer.
        typeSizer.Add(forecastText, flag=wx.LEFT|wx.TOP|wx.ALIGN_LEFT,
            border=5)
        typeSizer.AddSpacer(25)
        typeSizer.Add(buttonOne, flag=wx.TOP, border=5)
        typeSizer.AddSpacer(15)
        typeSizer.Add(buttonTwo, flag=wx.TOP, border=5)
        typeSizer.AddSpacer(15)
        typeSizer.Add(buttonThree, flag=wx.TOP, border=5)

        # Create the forecast list control.
        self.forecastList = wx.ListCtrl(self, size=(-1, 60),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.forecastList.InsertColumn(0, "January")
        self.forecastList.InsertColumn(1, "February")
        self.forecastList.InsertColumn(2, "March")
        self.forecastList.InsertColumn(3, "April")
        self.forecastList.InsertColumn(4, "May")
        self.forecastList.InsertColumn(5, "June")
        self.forecastList.InsertColumn(6, "July")
        self.forecastList.InsertColumn(7, "August")
        self.forecastList.InsertColumn(8, "September")
        self.forecastList.InsertColumn(9, "October")
        self.forecastList.InsertColumn(10, "November")
        self.forecastList.InsertColumn(11, "December")

        # Add everything to the forecast sizer.
        forecastSizer.Add(typeSizer)
        forecastSizer.Add(self.forecastList, flag=wx.ALL|wx.ALIGN_RIGHT,
            border=5)

        ## History
        # Create the history sizer.
        historySizer = wx.BoxSizer(wx.VERTICAL)

        # Create the history label.
        historyText=wx.StaticText(self, label="History")

        # Set the font for the history text.
        historyText.SetFont(infoFont)

        # Create the history list control.
        self.historyList = wx.ListCtrl(self, size=(-1, 200),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.historyList.InsertColumn(0, "Year", width=50)
        self.historyList.InsertColumn(1, "January")
        self.historyList.InsertColumn(2, "February")
        self.historyList.InsertColumn(3, "March")
        self.historyList.InsertColumn(4, "April")
        self.historyList.InsertColumn(5, "May")
        self.historyList.InsertColumn(6, "June")
        self.historyList.InsertColumn(7, "July")
        self.historyList.InsertColumn(8, "August")
        self.historyList.InsertColumn(9, "September")
        self.historyList.InsertColumn(10, "October")
        self.historyList.InsertColumn(11, "November")
        self.historyList.InsertColumn(12, "December")

        # Add everything to the history sizer.
        historySizer.Add(historyText, flag=wx.LEFT|wx.TOP|wx.ALIGN_LEFT,
            border=5)
        historySizer.Add(self.historyList, flag=wx.ALL|wx.ALIGN_RIGHT,
            border=5)

        ## Panel Operations
        # Add everything to the master sizer.
        masterSizer.Add(productSizer, flag=wx.EXPAND)
        masterSizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
        masterSizer.Add(forecastSizer, flag=wx.EXPAND)
        masterSizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
        masterSizer.Add(historySizer, flag=wx.EXPAND)

        # Set the master sizer for the panel.
        self.SetSizer(masterSizer)

    def setProduct(self, product):
        """
        """

        ## Product Information
        # Set the variable to be the updated product.
        self.product = product

        # Get the data for the product from the database.
        data = isql.getProduct(product)

        # Set the labels for the static texts.
        self.nameText.SetLabel(data[0])
        self.accountText.SetLabel(data[2])
        self.classText.SetLabel(data[3])
        self.categoryText.SetLabel(data[4])
        #self.subcategoryText.SetLabel(data[5])

        ## Product Variables
        # Get the variables.
        variables = idata.hasVariables(data[0], convert=True)

        # Remove nonvariables.
        variables = [x for x in variables if x[-8:] == " Monthly"]
        try:
            variables.remove("Forecast")
        except ValueError:
            pass

        # Get the latest data dates.
        latest = idata.latestData(data[0], variables, convert=True)

        # Get the number of observations.
        count = idata.obsCount(data[0], variables, convert=True)

        # Remove all items from the variables list.
        self.variablesList.DeleteAllItems()

        # Add the new items to the variables list.
        index = 0
        for variable in variables:
            self.variablesList.InsertStringItem(index,
                variable[0 : len(variable) - 8])
            self.variablesList.SetStringItem(index, 1, latest[index])
            self.variablesList.SetStringItem(index, 2, str(count[index]))
            index += 1

        ## Related Products
        # Get the related products.
        related = isql.getData({"class": data[3], "category": data[4],
            "subcategory": data[5]})

        # Extract only the names of the related products.
        related = [x[0] for x in related]

        # Remove itself from the related list.
        related.remove(data[0])

        # Set the items for the related list.
        self.relatedList.SetItems(related)

        ## Linked Products
        # Get the linked products.
        linked = isql.getLinksTo(product)

        # Set the items for the linked list.
        self.linkedList.SetItems(linked)

        ## History
        # Get the historical values.
        history = idata.getData(product, "finished_goods_monthly")

        # Remove all items from the forecast and history list.
        self.forecastList.DeleteAllItems()
        self.historyList.DeleteAllItems()

        # Convert the data into overlapped form.
        try:
            historyOverlap = pm.overlap(history)
        except IndexError:
            historyOverlap = []
            hError = wx.MessageDialog(self, "Historical data not available.",
                style=wx.ICON_ERROR)
            hError.ShowModal()

            self.Layout()
            return

        # Determine the years in the data.
        start = int(history[0][0][0 : 4])
        end = int(history[-1][0][0 : 4])
        years = list(range(start, end + 1))

        # Iterate over the data and add it to the list control.
        index1 = 0
        for row in historyOverlap:
            self.historyList.InsertStringItem(index1,
                "{:d}".format(years[index1]))
            index2 = 1
            for col in row:
                if np.isnan(col):
                    self.historyList.SetStringItem(index1, index2, '')
                else:
                    self.historyList.SetStringItem(index1, index2,
                        "{:.0f}".format(col))
                index2 += 1
            index1 += 1

        ## Forecast
        # Get the forecast values.
        forecast = idata.getForecast(product, method=self.modelType)

        # Get todays date.
        today = dt.date(1, 1, 1).today()

        # Add the row that will contain the forecasts.
        self.forecastList.InsertStringItem(0, "")

        # Add each forecast for all months.
        for month in range(1, 13):
            if month > today.month:
                year = today.year
            else:
                year = today.year + 1
            try:
                self.forecastList.SetStringItem(0, month - 1,
                    "{:.0f}".format(forecast[dt.datetime(year, month, 1)]))
            except KeyError:
                continue

        # Relayout the panel.
        self.Layout()

    def getProduct(self):
        """
        """

        return self.product

    def onRadioButton(self, event, modelType):
        """
        """

        # Set the model type for the class.
        self.modelType = modelType

        # Remove the old values from the forecast list.
        self.forecastList.DeleteAllItems()

        # Get the forecast values.
        forecast = idata.getForecast(self.product, method=modelType)

        # Get todays date.
        today = dt.date(1, 1, 1).today()

        # Add the row that will contain the forecasts.
        self.forecastList.InsertStringItem(0, "")

        # Add each forecast for all months.
        for month in range(1, 13):
            if month > today.month:
                year = today.year
            else:
                year = today.year + 1
            try:
                self.forecastList.SetStringItem(0, month - 1,
                    "{:.0f}".format(forecast[dt.datetime(year, month, 1)]))
            except KeyError:
                continue

        # Relayout the panel.
        self.Layout()

    def onVariable(self, event):
        """
        """

        # Get the variable selected.
        variable = self.variablesList.GetItemText(self.variablesList.\
            GetFirstSelected())

        # Create the data viewer for the variable.
        dv.DataViewer(self.nameText.GetLabel(), variable + "_monthly", self)

    def onRelated(self, event):
        """
        """

        # Set the product to be the selected.
        self.setProduct(self.relatedList.GetString(self.relatedList.\
            GetSelection()))
