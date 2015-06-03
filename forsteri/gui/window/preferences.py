#!/usr/bin/python

"""
Preferences Frame

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
        super(PreferencesFrame, self).__init__(*args, **kwargs)

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
        masterSizer.AddSpacer(9)
        masterSizer.Add(wx.StaticLine(masterPanel, size=(585, 2)),
            flag=wx.ALIGN_CENTER)
        masterSizer.AddSpacer(9)
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
