import csv
import subprocess
import webbrowser
import wx
import wx.html
import wx.adv

class OpenFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(OpenFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create the master panel.
        self.masterPanel = wx.Panel(self)

        # Create the master sizer.
        self.masterSizer = wx.GridBagSizer(5, 5)

        # Set the initial variables.
        self.currentSelect = "Account"
        self.subCombos = []

        """Initialize the radio buttons."""
        # Set comonly used variables.
        buttonLabels = ["Account", "Class", "Component", "Chemical"]
        labelLen = len(buttonLabels)

        # Create the radio buttons in an array.
        radioButtons = [wx.RadioButton(self.masterPanel, label=buttonLabels[0],
            style=wx.RB_GROUP)]
        for i in range(1, labelLen):
            radioButtons.append(wx.RadioButton(self.masterPanel,
                label=buttonLabels[i]))

        # Create the static box and its sizer.
        staticBox = wx.StaticBox(self.masterPanel, label="Search by")
        rbSizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)

        # Set the radio button flag.
        rbFlag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER

        # Add the radio buttons to the box sizer and bind them to actions.
        for j in range(0, labelLen):
            rbSizer.Add(radioButtons[j], flag=rbFlag, border=10)
            self.Bind(wx.EVT_RADIOBUTTON, lambda event, select=buttonLabels[j]:
                self.setSearch(event, select), radioButtons[j])

        # Add the box sizer to the master sizer.
        self.masterSizer.Add(rbSizer, pos=(0, 0), span=(1, 5), flag=rbFlag,
            border=10)

        """Initialize the combo boxes."""
        # Get the choice list.
        accounts = self.getComboList(self.currentSelect.lower())

        # Set the combo box flag.
        cbFlag = wx.ALL | wx.EXPAND

        # Create the initial text and combo box.
        self.topText = wx.StaticText(self.masterPanel,
            label=self.currentSelect)
        self.topBox = wx.ComboBox(self.masterPanel, choices=accounts,
            style=wx.CB_READONLY)

        # Add the text and combo box to the master sizer.
        self.masterSizer.Add(self.topText, pos=(1, 0), flag=cbFlag, border=10)
        self.masterSizer.Add(self.topBox, pos=(1, 1), span=(1, 4), flag=cbFlag,
            border=5)

        # Bind the selection of a combo box to an action.
        self.Bind(wx.EVT_COMBOBOX, self.drawNextComboBox, self.topBox)

        """Initialize the buttons."""
        # Create the open and cancel buttons.
        openButton = wx.Button(self.masterPanel, id=wx.ID_OPEN, label="&Open")
        cancelButton = wx.Button(self.masterPanel, id=wx.ID_CANCEL,
            label="&Cancel")
        openButton.SetFocus()

        # Add the buttons to the master sizer.
        bFlag = wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM
        self.masterSizer.Add(openButton, pos=(5, 0), flag=bFlag, border=10)
        self.masterSizer.Add(cancelButton, pos=(5, 4), flag=bFlag, border=10)

        # Set the bindings for actions when a button is clicked.
        self.Bind(wx.EVT_BUTTON, self.onOpen, openButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelButton)

        # Make the sizer dynamic.
        self.masterSizer.AddGrowableCol(2)
        self.masterSizer.AddGrowableRow(0)

        # Set the sizer for the main panel.
        self.masterPanel.SetSizer(self.masterSizer)

        # Set window properties.
        self.SetSize((500, 325))
        self.SetTitle("Open Forecast")
        self.Centre()
        self.Show(True)

    def drawNextComboBox(self, event):
        pass

    def setSearch(self, event, select):
        # Set the current selection to select.
        self.currentSelect = select

        # Remove any sub combo boxes from the sizer.
        for cb in self.subCombos:
            self.masterSizer.Remove(cb)
        self.masterSizer.Layout()

        # Set the selection text to empty and remove the choices.
        self.topBox.SetSelection(0)
        self.topBox.Clear()

        # Change the top level text to be what was selected.
        self.topText.SetLabel(select)

        # Add the correct choices to the top combo box.
        self.topBox.Append(self.getComboList(select.lower()))

    def onOpen(self, event):
        print("Opening")

    def onCancel(self, event):
        self.Close()

    def setComboList(self, type):
        pass

    def getComboList(self, source):
        # Initialize list.
        lst = []

        # Pull accounts from data
        with open("../../data/" + source + ".csv", newline='') as csvFile:
            fileReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in fileReader:
                lst.append(row)

        # Return just the first row.
        lst = lst[0]
        lst.insert(0, "")
        return lst

def main():
    app = wx.App()
    OpenFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
