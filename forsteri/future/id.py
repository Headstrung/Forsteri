#!/usr/bin/python

"""
Import Data Frame

Copyright (C) 2014, 2015 by Andrew Chalres Hawkins

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

"""
Import Declarations
"""
import datetime as dt
import decompose as dec
import idata
import ihdf5
import pandas as pd
import wx

"""
Constant Declarations
"""
DATA_DIR = "/home/andrew/Dropbox/product-quest/Forsteri/data/"

"""
Frame Class
"""
class ImportFrame(wx.Frame):
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
          ManagerFrame
        """

        ## Frame
        # Initialize by the parent's constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## File Type Selection
        # Create the file type sizer.
        fileTypeSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the file type radio buttons.
        self.timeseriesRB = wx.RadioButton(masterPanel, label="Timeseries",
            style=wx.RB_GROUP)
        singleRB = wx.RadioButton(masterPanel, label="Single Time")

        # Add the radio buttons to the file type sizer.
        fileTypeSizer.AddMany([self.timeseriesRB, (75, 0), singleRB])

        # Bind the radio buttons to functions.
        self.timeseriesRB.Bind(wx.EVT_RADIOBUTTON, self.onFile)
        singleRB.Bind(wx.EVT_RADIOBUTTON, self.onFile)

        ## Input Static Boxes.
        # Create the input sizer.
        inputSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Timeseries
        # Create the timeseries static box.
        timeseriesSB = wx.StaticBox(masterPanel, label="Timeseries")

        # Create the timeseries sizer.
        timeseriesSizer = wx.StaticBoxSizer(timeseriesSB, wx.VERTICAL)

        # Get the choices for the date format and variable name selection.
        dfChoices = ihdf5.getDateFormats()
        vnChoices = idata.getVariables()
        currentDate = dt.date(1, 1, 1).today()

        # Create the date format and variable name combo boxes, check box, and
        # labels.
        dfLabel = wx.StaticText(masterPanel, label="Date Format")
        vnLabel = wx.StaticText(masterPanel, label="Variable")
        self.dfEntry = wx.ComboBox(masterPanel, size=(150, -1),
            choices=dfChoices, style=wx.CB_READONLY|wx.CB_SORT)
        self.vnEntry = wx.ComboBox(masterPanel, size=(150, -1),
            choices=vnChoices, style=wx.CB_READONLY|wx.CB_SORT)
        self.dahCheck = wx.CheckBox(masterPanel, label="Dates as Headers")

        # Set the initial combo box selections.
        self.dfEntry.SetSelection(0)
        self.vnEntry.SetSelection(0)

        # Add everything to the timeseries sizer.
        timeseriesSizer.AddSpacer(5)
        timeseriesSizer.Add(dfLabel, flag=wx.ALIGN_CENTER)
        timeseriesSizer.Add(self.dfEntry, flag=wx.LEFT|wx.RIGHT|
            wx.ALIGN_CENTER, border=5)
        timeseriesSizer.AddSpacer(5)
        timeseriesSizer.Add(self.dahCheck, flag=wx.ALIGN_CENTER)
        timeseriesSizer.AddSpacer(5)
        timeseriesSizer.Add(vnLabel, flag=wx.ALIGN_CENTER)
        timeseriesSizer.Add(self.vnEntry, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|
            wx.ALIGN_CENTER, border=5)

        # Bind the combo boxes and check box to functions.
        self.dfEntry.Bind(wx.EVT_COMBOBOX, self.onFile)
        self.vnEntry.Bind(wx.EVT_CHECKBOX, self.onFile)
        self.dahCheck.Bind(wx.EVT_CHECKBOX, self.onFile)

        ## Single Time
        # Create the single time static box.
        singleTimeSB = wx.StaticBox(masterPanel, label="Single Time")

        # Create the single time sizer.
        singleTimeSizer = wx.StaticBoxSizer(singleTimeSB, wx.VERTICAL)

        # Create the date text sizer.
        dateTextSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the static text.
        self.dateText = [wx.StaticText(masterPanel, label="Year"),
            wx.StaticText(masterPanel, label="Month"),
            wx.StaticText(masterPanel, label="Day")]

        # Add the date text to the date text sizer.
        spacers = [(30, 0), (38, 0), (27, 0)]
        index = 0
        for text in self.dateText:
            # Add each static text with a spacer value.
            dateTextSizer.AddMany([spacers[index], text])

            # Increment the index.
            index += 1

        # Create the date entry sizer.
        dateEntrySizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the date entry forms.
        self.stEntry = [wx.SpinCtrl(masterPanel, value=str(currentDate.year),
            min=2000, max=currentDate.year, size=(75, -1))]
        self.stEntry.append(wx.SpinCtrl(masterPanel,
            value=str(currentDate.month), min=1, max=12, size=(50, -1)))
        self.stEntry.append(wx.SpinCtrl(masterPanel,
            value=str(currentDate.day), min=1, max=31, size=(50, -1)))

        # Add the date entry forms the date entry sizer.
        for entry in self.stEntry:
            dateEntrySizer.Add(entry, flag=wx.LEFT|wx.RIGHT, border=5)

        # Add everything to the single time sizer.
        singleTimeSizer.AddSpacer(5)
        singleTimeSizer.Add(dateTextSizer, flag=wx.ALIGN_LEFT)
        singleTimeSizer.Add(dateEntrySizer, flag=wx.BOTTOM|wx.ALIGN_CENTER,
            border=5)

        # Add everything to the input sizer.
        inputSizer.Add(timeseriesSizer)
        inputSizer.AddSpacer(5)
        inputSizer.Add(singleTimeSizer)

        ## File Selection
        # Create the file picker sizer.
        filePickerSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the file picker text.
        filePickerText = wx.StaticText(masterPanel, label="File Location")

        # Create the file picker control.
        self.filePicker = wx.FilePickerCtrl(masterPanel, path='',
            wildcard="CSV files (*.csv)|*.csv|TXT files (*txt)|*.txt",
            size=(250, -1), style=wx.FLP_FILE_MUST_EXIST)
        self.filePicker.SetInitialDirectory(DATA_DIR)

        # Add the text and file picker to the file picker sizer.
        filePickerSizer.Add(filePickerText)
        filePickerSizer.Add(self.filePicker)

        # Bind the selection of a file to a function.
        self.filePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFile)

        ## File Analyzer
        # Create the header static box.
        headerSB = wx.StaticBox(masterPanel, label="Header Information")

        # Create the header sizer.
        headerSizer = wx.StaticBoxSizer(headerSB, wx.VERTICAL)

        # Create the list control.
        self.headerList = wx.ListCtrl(masterPanel, size=(544, 300),
            style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|wx.BORDER_SUNKEN)

        # Add columns to the list control.
        self.headerList.InsertColumn(0, "Original", width=170)
        self.headerList.InsertColumn(1, "Changed", width=170)
        self.headerList.InsertColumn(2, "Reason", width=170)

        # Add the header list to the header sizer.
        headerSizer.Add(self.headerList)

        ## Finish Buttons
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        importButton = wx.Button(masterPanel, label="&Import")
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the import button to be the default button.
        importButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([importButton, (5, 0), cancelButton])

        # Bind button presses to functions.
        importButton.Bind(wx.EVT_BUTTON, self.onImport)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        ## Frame Operations
        # Add everything to the master sizer.
        masterSizer.AddSpacer(5)
        masterSizer.Add(fileTypeSizer, flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(10)
        masterSizer.Add(inputSizer, flag=wx.ALIGN_CENTER)
        masterSizer.Add(filePickerSizer)
        masterSizer.Add(headerSizer)
        masterSizer.Add(finishSizer)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Bind closing the frame to a function.
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set window properties.
        self.SetSize((575, 565))
        self.SetTitle("Import Data")
        self.Centre()
        self.Show(True)

    """
    Helper Functions
    """
    def displayChange(self, source, dateFormat):
        """
        """

        # Decompose the file and extract the old and new headers.
        (oldHeaders, self.newHeaders, self.hasDate, self.firstDate) =\
            dec.decompose(source, dateFormat)

        # Create missing and ignored boolean lists.
        reason = []
        index = 0
        for header in self.newHeaders:
            if header != "Missing" and header != "Ignore":
                reason.append("Match")
            else:
                reason.append(header)
                self.newHeaders[index] = ''

            # Increment the index.
            index += 1

        # Remove all items from the list control and reset the index.
        self.headerList.DeleteAllItems()
        index = 0

        # Add the items to the list control.
        for oldHeader in oldHeaders:
            # Add the items to the list control.
            self.headerList.InsertItem(index, oldHeader)
            if self.newHeaders[index] == "Date":
                self.headerList.SetItem(index, 1,
                    str(self.newHeaders[index]) + ": " + str(self.firstDate))
            else:
                self.headerList.SetItem(index, 1, str(self.newHeaders[index]))
            self.headerList.SetItem(index, 2, reason[index])

            # Increment the index.
            index += 1

        return True

    """
    Event Handler Functions
    """
    def onFile(self, event):
        """
        """

        # Enable and disable the necessary widgets.
        if self.timeseriesRB.GetValue():
            # Enable the timeseries and disable the single time selections.
            self.dateText[0].Enable()
            self.dfEntry.Enable()
            for index in range(0, 3):
                self.dateText[index + 1].Disable()
                self.stEntry[index].Disable()
        else:
            # Enable the single time and disable the timeseries selections.
            self.dateText[0].Disable()
            self.dfEntry.Disable()
            for index in range(0, 3):
                self.dateText[index + 1].Enable()
                self.stEntry[index].Enable()

        # Get the file locations on the disk.
        source = self.filePicker.GetPath()

        # If the source is an empty string, return.
        if source == '':
            return
        else:
            # Route the file type to the proper input function.
            if self.timeseriesRB.GetValue():
                # Get the value selected for date format from the combo box.
                dateFormat = self.dfEntry.GetValue()
            else:
                # Get the values input for the date of the file.
                date = dt.date(self.stEntry[0].GetValue(),
                    self.stEntry[1].GetValue(), self.stEntry[2].GetValue())

                dateFormat = ''

            # Display the headers, what they were changed to, and why.
            self.displayChange(source, dateFormat)

    def onImport(self, event):
        """
        """

        # Check to make sure there is a date for the file.
        if self.timeseriesRB.GetValue():
            if ("Date" in self.newHeaders or self.hasDate) and self.firstDate:
                # Good input for timeseries.
                # Get the file locations on the disk.
                source = self.filePicker.GetPath()

                # Get the value selected for date format from the combo box.
                dateFormat = self.dfEntry.GetValue()

                # Run the decompose again to get the full data.
                dec.decomposeCut(source, dateFormat)

                # Read the file created by decompose with pandas.
                data = pd.read_csv(source[:-4] + "-cut.csv")

                # Convert date into date objects.
                for date in data["Date"]:
                    date = dec.checkDate(str(date), dateFormat)
                    print(date)
                print(data["Date"])
            else:
                # Bad input for timeseries.
                errorDialog = wx.MessageDialog(self,
                    "There was an issue with the date column(s). Consider " +
                    "switching to single time or revising the date format.",
                    "Error",
                    wx.OK|wx.ICON_ERROR)
                errorDialog.ShowModal()

                return
        else:
            if "Date" in self.newHeaders or self.hasDate:
                # Bad input for single time.
                errorDialog = wx.MessageDialog(self,
                    "There was an issue with the date of the file. Consider " +
                    "switching to timeseries.",
                    "Error",
                    wx.OK|wx.ICON_ERROR)
                errorDialog.ShowModal()

                return
            elif len([x for x in self.newHeaders if x != '']) == 1:
                # Bad input for single time.
                errorDialog = wx.MessageDialog(self,
                    "There are too few variables to be imported. Consider " +
                    "switching to timeseries.",
                    "Error",
                    wx.OK|wx.ICON_ERROR)
                errorDialog.ShowModal()

                return
            else:
                # Good input for single time.
                pass

        # Add missing values to the HDF5 file.


    def onCancel(self, event):
        """
        """

        self.Close()

    def onClose(self, event):
        """
        """

        self.Destroy()

"""
Start Application
"""
def main():
    """
    When the file is called independently create and display the manager frame.
    """

    app = wx.App()
    ImportFrame(None, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
