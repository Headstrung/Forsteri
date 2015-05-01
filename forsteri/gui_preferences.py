#!/usr/bin/python

"""
Preferences Frame

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
import pickle
import wx

"""
Constant Declarations
"""


"""
Frame Class
"""
class PreferencesFrame(wx.Frame):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        ## Panel
        # Initialize the parents constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## Reporting
        # Create the reporting static box.
        reportSB = wx.StaticBox(masterPanel, label="Reporting")

        # Create the reporting sizer.
        reportSizer = wx.StaticBoxSizer(reportSB, wx.VERTICAL)

        # Create the first rows sizer.
        row1Sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the label for the first row.
        row1Label = wx.StaticText(masterPanel, label="Forecast Type")

        # Create the list of choices for the first row.
        choice1 = ["Auto", "MLR", "EMA", "Naive"]

        # Create the object for the first row.
        self.row1Obj = wx.ComboBox(masterPanel, size=(150, -1),
            choices=choice1, style=wx.CB_READONLY)

        # Add the contents to the row 1 sizer.
        row1Sizer.Add(row1Label, flag=wx.ALIGN_CENTER|wx.RIGHT, border=5)
        row1Sizer.Add(self.row1Obj, flag=wx.ALIGN_CENTER)

        # Add all rows to the report sizer.
        reportSizer.Add(row1Sizer, flag=wx.ALL, border=5)

        # 


        ## Finish Buttons
        # Create the finish sizer.
        finishSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons.
        okButton = wx.Button(masterPanel, id=wx.ID_OK)
        cancelButton = wx.Button(masterPanel, id=wx.ID_CANCEL)

        # Set the OK button to be the dafault button.
        okButton.SetDefault()

        # Add the buttons to the finish sizer.
        finishSizer.AddMany([okButton, (5, 0), cancelButton, (5, 0)])

        # Bind button presses to functions.
        okButton.Bind(wx.EVT_BUTTON, self.onOK)
        cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

        ## Panel Operations
        # Add everything to the master sizer.
        masterSizer.Add(reportSizer, flag=wx.ALL, border=5)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(590, 20)),
            flag=wx.ALIGN_CENTER)
        masterSizer.Add(finishSizer,
            flag=wx.BOTTOM|wx.ALIGN_RIGHT, border=5)

        # Load the prefernces.
        self.loadPref()

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Bind closing the frame to a function.
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set window properties.
        self.SetSize((600, 400))
        self.SetTitle("Preferences")
        self.Centre()
        self.Show(True)

    """
    Helper Functions
    """
    def loadPref(self):
        """
        """

        # Load the preferences from the pickle file.
        pref = pickle.load(open("../data/pref.p", "rb"))

        # Set all of the prefernce objects.
        self.row1Obj.SetValue(pref["report_type"])

        return True

    def savePref(self):
        """
        """

        # Initialize the preferences dictionary.
        pref = {}

        # Get all of the preference objects data.
        pref["report_type"] = self.row1Obj.GetValue()

        # Save the preferences into the pickle file.
        pickle.dump(pref, open("../data/pref.p", "wb"))

        return True

    """
    Event Handlers
    """
    def onOK(self, event):
        """
        """

        # Save the preferences.
        self.savePref()

        self.Close()

    def onCancel(self, event):
        """
        """

        self.Close()

    def onClose(self, event):
        """
        """

        self.Destroy()



def main():
    """
    When the file is called independently create and display the manager frame.
    """

    app = wx.App()
    PreferencesFrame(None, style=wx.DEFAULT_FRAME_STYLE)#^wx.RESIZE_BORDER)
    app.MainLoop()

if __name__ == '__main__':
    main()
