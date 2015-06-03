#!/usr/bin/python

"""
Import Data Frame

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
import datetime as dt
import threading as td
import wx

from forsteri.interface import data as idata
from forsteri.interface import sql as isql
from forsteri.process import bring as dec

"""
Constant Declarations
"""


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
        super(ImportFrame, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## File Type
        # Create the file static box.
        fileSB = wx.StaticBox(masterPanel, label="File Information")

        # Create the file sizer.
        fileSizer = wx.StaticBoxSizer(fileSB, wx.VERTICAL)

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

        ## Date
        # Create the date text sizer.
        dateTextSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the static text.
        self.dateText = [wx.StaticText(masterPanel, label="Date Format"),
            wx.StaticText(masterPanel, label="Year"),
            wx.StaticText(masterPanel, label="Month"),
            wx.StaticText(masterPanel, label="Day")]

        # Add the date text to the date text sizer.
        spacers = [(50, 0), (85, 0), (35, 0), (20, 0)]
        index = 0
        for text in self.dateText:
            # Add each static text with a spacer value.
            dateTextSizer.AddMany([spacers[index], text])

            # Set only the date entry to be disabled.
            if index > 0:
                text.Disable()

            # Increment the index.
            index += 1

        # Create the date entry sizer.
        dateEntrySizer = wx.BoxSizer(wx.HORIZONTAL)

        # Get the choices for timeseries selection.
        choices = [date[1:] for date in isql.getForVariable("Date") if
            date[0] == '$']
        currentDate = dt.date(1, 1, 1).today()

        # Create the date entry forms.
        self.dfEntry = wx.ComboBox(masterPanel, size=(150, -1),
            choices=choices, style=wx.CB_READONLY|wx.CB_SORT)
        self.stEntry = [wx.SpinCtrl(masterPanel, value=str(currentDate.year),
            min=2000, max=currentDate.year, size=(75, -1))]
        self.stEntry.append(wx.SpinCtrl(masterPanel,
            value=str(currentDate.month), min=1, max=12, size=(50, -1)))
        self.stEntry.append(wx.SpinCtrl(masterPanel,
            value=str(currentDate.day), min=1, max=31, size=(50, -1)))

        # Set the initial combo box selection.
        self.dfEntry.SetSelection(0)

        # Set the date entry forms to be disabled.
        for index in range(0, 3):
            self.stEntry[index].Disable()

        # Bind the combo box selection to a function.
        self.dfEntry.Bind(wx.EVT_COMBOBOX, self.onFile)

        # Add the date entry items to the sizer.
        dateEntrySizer.AddMany([self.dfEntry, (25, 0), self.stEntry[0],
            (5, 0), self.stEntry[1], (5, 0), self.stEntry[2]])

        ## Last Selection
        # Create the last selection sizer.
        lastSizer = wx.BoxSizer(wx.HORIZONTAL)

        ## File Picker
        # Create the file picker sizer.
        filePickerSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the file picker text.
        filePickerText = wx.StaticText(masterPanel, label="File Location")

        # Create the file picker control.
        self.filePicker = wx.FilePickerCtrl(masterPanel, path='',
            wildcard="CSV files (*.csv)|*.csv|TXT files (*txt)|*.txt",
            size=(250, -1), style=wx.FLP_FILE_MUST_EXIST)
        self.filePicker.SetInitialDirectory(idata.DATA)

        # Add the text and file picker to the file picker sizer.
        filePickerSizer.Add(filePickerText, flag=wx.ALIGN_CENTER)
        filePickerSizer.Add(self.filePicker, flag=wx.LEFT, border=5)

        # Bind the selection of a file to a function.
        self.filePicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.onFile)

        ## Check Boxes
        # Create the check sizer.
        checkSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the check boxes.
        self.shiftCheck = wx.CheckBox(masterPanel, label="Shift Week")
        self.overwriteCheck = wx.CheckBox(masterPanel, label="Overwrite")

        # Initially disable the Walmart week check box.
        self.shiftCheck.Disable()

        # Bind check boxes to functions.
        self.shiftCheck.Bind(wx.EVT_CHECKBOX, self.onFile)

        # Add the check boxes to the sizer.
        checkSizer.Add(self.shiftCheck, flag=wx.RIGHT|wx.ALIGN_LEFT, border=5)
        checkSizer.Add(self.overwriteCheck,
            flag=wx.TOP|wx.RIGHT|wx.ALIGN_LEFT, border=5)

        # Add the file picker and check sizers to the last sizer.
        lastSizer.Add(filePickerSizer)
        lastSizer.AddSpacer(25)
        lastSizer.Add(checkSizer)

        # Add everything to the file sizer.
        fileSizer.Add(fileTypeSizer, flag=wx.TOP|wx.ALIGN_CENTER, border=5)
        fileSizer.AddSpacer(10)
        fileSizer.Add(dateTextSizer, flag=wx.ALIGN_LEFT)
        fileSizer.Add(dateEntrySizer, flag=wx.ALIGN_CENTER)
        fileSizer.AddSpacer(10)
        fileSizer.Add(lastSizer, flag=wx.BOTTOM|wx.ALIGN_CENTER, border=5)

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
        headerSizer.Add(self.headerList, flag=wx.ALL, border=5)

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
        masterSizer.Add(fileSizer, flag=wx.TOP|wx.ALIGN_CENTER, border=5)
        masterSizer.Add(headerSizer, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        masterSizer.Add(finishSizer, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT,
            border=5)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Bind closing the frame to a function.
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set window properties.
        self.SetSize((575, 580))
        self.SetTitle("Import Data")
        self.Centre()
        self.Show(True)

    """
    Helper Functions
    """
    def displayChange(self, source, dateFormat):
        """
        Show the old headers, what they were changed to, and why in the list
        control.

        Args:
          source (str): The location of the file on the disk.
          dateFormat (str): The format of the date(s).

        Returns:
          bool: True if successful, false otherwise.
        """

        # Get the shift check.
        shift = self.shiftCheck.GetValue()

        # Decompose the file and extract the old and new headers.
        (oldHeaders, self.newHeaders, self.hasDate, self.firstDate) =\
            dec.decompose(source, dateFormat, shift)

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
            self.headerList.InsertStringItem(index, oldHeader)
            if self.newHeaders[index] == "Date":
                self.headerList.SetStringItem(index, 1,
                    str(self.newHeaders[index]) + ": " + str(self.firstDate))
            else:
                self.headerList.SetStringItem(index, 1,
                    str(self.newHeaders[index]))
            self.headerList.SetStringItem(index, 2, reason[index])

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

            # If a date format with week in it is selected enable walmart week.
            if 'w' in self.dfEntry.GetValue():
                self.shiftCheck.Enable()
            else:
                self.shiftCheck.Disable()
        else:
            # Enable the single time and disable the timeseries selections.
            self.dateText[0].Disable()
            self.dfEntry.Disable()
            self.shiftCheck.Disable()
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

        # Get the file locations on the disk.
        source = self.filePicker.GetPath()

        # Get whether or not to overwrite.
        overwrite = self.overwriteCheck.GetValue()

        # If no source has been selected, show an error message and return.
        if source == '':
            errorDialog = wx.MessageDialog(self,
                "No input file was selected. Please select a file.", "Error",
                wx.OK|wx.ICON_ERROR)
            errorDialog.ShowModal()

            return

        # Check to make sure there is a date for the file.
        if self.timeseriesRB.GetValue():
            # Get the value selected for date format from the combo box.
            dateFormat = self.dfEntry.GetValue()

            if ("Date" in self.newHeaders or self.hasDate) and self.firstDate:
                # Check if there is a date in the headers.
                if type(self.newHeaders[-1]) == dt.date or\
                    type(self.newHeaders[-2]) == dt.date:
                    # Remove any empty strings from the headers list.
                    self.newHeaders = list(filter(('').__ne__,
                        self.newHeaders))

                    # Check if there are any repeat dates.
                    if len(self.newHeaders) != len(set(self.newHeaders)):
                        errorDialog = wx.MessageDialog(self,
                        "There are repeated dates in the header. Please " +
                        "consider reformatting.", "Error", wx.OK|wx.ICON_ERROR)
                        errorDialog.ShowModal()

                        return

                    # Create the variable selection dialog box.
                    variableDlg = VariableDialog(self)

                    # Show the variable dialog box.
                    if variableDlg.ShowModal() == wx.ID_CANCEL:
                        return

                    # Get the variable selected.
                    variable = variableDlg.getSelection()

                    # Destroy the variable dialog.
                    variableDlg.Destroy()

                    # Call the import timeseries function in a thread.
                    importThread = td.Thread(target=dec.importTimeseries,
                        args=(source, dateFormat, variable, overwrite))
                    importThread.start()

                    self.Close()
                else:
                    # Get the shift check.
                    shift = self.shiftCheck.GetValue()

                    # Call the import timeseries function in a thread.
                    importThread = td.Thread(target=dec.importTimeseries2,
                        args=(source, dateFormat, overwrite, shift))
                    importThread.start()

                    self.Close()
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
                # Get the date from the input.
                date = dt.date(*(entry.GetValue() for entry in self.stEntry))

                # Call the import timeseries function in a thread.
                importThread = td.Thread(target=dec.importSingleTime,
                    args=(source, date, overwrite))
                importThread.start()

                self.Close()

    """
    Helper Functions
    """
    def convertVariable(self, variable):
        """
        """

        varTemp = variable

        return varTemp.replace(' ', '_').lower()

    """
    Event Handler Functions
    """
    def onCancel(self, event):
        """
        """

        self.Close()

    def onClose(self, event):
        """
        """

        self.Destroy()

class VariableDialog(wx.Dialog):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        # Initialize by the parent's constructor.
        super(VariableDialog, self).__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the text to inform the user.
        text = wx.StaticText(masterPanel, label="Please select the " +\
            "appropriate variable that\n\t\t  represents the file.")

        # Get the list of variable choices.
        choices = self.getChoices()

        # Create the variable combo box.
        self.varCombo = wx.ComboBox(masterPanel, size=(150, -1),
            choices=choices, style=wx.CB_READONLY|wx.CB_SORT)

        # Set the initial combo box selection.
        self.varCombo.SetSelection(0)

        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the finish buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Add the finish buttons to the sizer.
        finishSizer.AddMany([okButton, (5, 0), cancelButton])

        # Add the text and combo box to the sizer.
        masterSizer.Add(text, flag=wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER,
            border=5)
        masterSizer.AddSpacer(10)
        masterSizer.Add(self.varCombo, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER,
            border=5)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(290, 20)),
            flag=wx.ALIGN_CENTER)
        masterSizer.Add(finishSizer, flag=wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT,
            border=5)

        # Set the master sizer.
        masterPanel.SetSizer(masterSizer)

        # Set the size of the window.
        self.SetSize((300, 155))

    def getChoices(self):
        """
        """

        # Get the list of variables.
        variables = isql.getVariables()

        # Convert each variable to be aestetically pleasing.
        #variables = [variable.replace('_', ' ').title() for variable in\
        #    variables]

        return variables

    def getSelection(self):
        """
        """

        # Get the value of the variable combo box.
        return self.varCombo.GetValue()

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
