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

        # Create the radio buttons to search by.
        self.rbAccount = wx.RadioButton(self.masterPanel, label="Account",
            style=wx.RB_GROUP)
        self.rbType = wx.RadioButton(self.masterPanel, label="Type")
        self.rbComponent = wx.RadioButton(self.masterPanel, label="Component")
        self.rbChemical = wx.RadioButton(self.masterPanel, label="Chemical")

        # Create the static sizer.
        staticBox = wx.StaticBox(self.masterPanel, label="Search by")
        rbSizer = wx.StaticBoxSizer(staticBox, wx.HORIZONTAL)

        # Add the radio buttons to the static sizer.
        rbFlag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER
        rbSizer.Add(self.rbAccount, flag=rbFlag, border=10)
        rbSizer.Add(self.rbType, flag=rbFlag, border=10)
        rbSizer.Add(self.rbComponent, flag=rbFlag, border=10)
        rbSizer.Add(self.rbChemical, flag=rbFlag, border=10)

        # Add the static sizer to the master sizer.
        self.masterSizer.Add(rbSizer, pos=(0, 0), span=(1, 5), flag=rbFlag,
            border=10)

        # Create the combo boxes for account.
        accounts = self.getComboList("account")
        self.cbText1 = wx.StaticText(self.masterPanel, label="Account")
        self.cbText2 = wx.StaticText(self.masterPanel, label="Product")
        self.cbText3 = wx.StaticText(self.masterPanel, label="")
        self.cbText4 = wx.StaticText(self.masterPanel, label="")
        self.combo1 = wx.ComboBox(self.masterPanel, choices=accounts,
            style=wx.CB_READONLY)
        self.combo2 = wx.ComboBox(self.masterPanel, choices=[],
            style=wx.CB_READONLY)
        self.combo3 = wx.ComboBox(self.masterPanel, choices=[],
            style=wx.CB_READONLY)
        self.combo4 = wx.ComboBox(self.masterPanel, choices=[],
            style=wx.CB_READONLY)

        # Add the combo boxes to the master sizer.
        cbFlag = wx.ALL | wx.EXPAND
        self.masterSizer.Add(self.cbText1, pos=(1, 0), flag=cbFlag, border=10)
        self.masterSizer.Add(self.cbText2, pos=(2, 0), flag=cbFlag, border=10)
        self.masterSizer.Add(self.cbText3, pos=(3, 0), flag=cbFlag, border=10)
        self.masterSizer.Add(self.cbText4, pos=(4, 0), flag=cbFlag, border=10)
        self.masterSizer.Add(self.combo1, pos=(1, 1), span=(1, 4), flag=cbFlag,
            border=5)
        self.masterSizer.Add(self.combo2, pos=(2, 1), span=(1, 4), flag=cbFlag,
            border=5)
        self.masterSizer.Add(self.combo3, pos=(3, 1), span=(1, 4), flag=cbFlag,
            border=5)
        self.masterSizer.Add(self.combo4, pos=(4, 1), span=(1, 4), flag=cbFlag,
            border=5)

        # Create the open and cancel buttons.
        openButton = wx.Button(self.masterPanel, id=wx.ID_OPEN, label="&Open")
        cancelButton = wx.Button(self.masterPanel, id=wx.ID_CANCEL,
            label="&Cancel")
        openButton.SetFocus()

        # Add the buttons to the master sizer.
        bFlag = wx.ALL | wx.EXPAND | wx.ALIGN_BOTTOM
        self.masterSizer.Add(openButton, pos=(5, 0), flag=bFlag, border=10)
        self.masterSizer.Add(cancelButton, pos=(5, 4), flag=bFlag, border=10)

        # Set the sizer for the main panel.
        self.masterSizer.AddGrowableCol(2)
        self.masterSizer.AddGrowableRow(0)
        self.masterPanel.SetSizer(self.masterSizer)

        # Bind button presses to functions.
        self.Bind(wx.EVT_RADIOBUTTON, self.setSearch, self.rbAccount)
        self.Bind(wx.EVT_RADIOBUTTON, self.setSearch, self.rbType)
        self.Bind(wx.EVT_RADIOBUTTON, self.setSearch, self.rbComponent)
        self.Bind(wx.EVT_RADIOBUTTON, self.setSearch, self.rbChemical)
        self.Bind(wx.EVT_COMBOBOX, self.onSelection, self.combo1)
        self.Bind(wx.EVT_COMBOBOX, self.onSelection, self.combo2)
        self.Bind(wx.EVT_COMBOBOX, self.onSelection, self.combo3)
        self.Bind(wx.EVT_COMBOBOX, self.onSelection, self.combo4)
        self.Bind(wx.EVT_BUTTON, self.onOpen, openButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelButton)

        # Set window properties.
        self.SetSize((480, 325))
        self.SetTitle("Open Forecast")
        self.Centre()
        self.Show(True)

    def setSearch(self, e):
        if self.rbAccount.GetValue() == True:
            accounts = self.getComboList("account")
            self.cbText1.SetLabel("Account")
            self.cbText2.SetLabel("Product")
            self.cbText3.SetLabel("")
            self.cbText4.SetLabel("")
            self.clearComboBoxes()
            self.combo1.Append(accounts)
        elif self.rbType.GetValue() == True:
            classes = self.getComboList("class")
            self.cbText1.SetLabel("Class")
            self.cbText2.SetLabel("Category")
            self.cbText3.SetLabel("Subcategory")
            self.cbText4.SetLabel("Product")
            self.clearComboBoxes()
            self.combo1.Append(classes)
        elif self.rbComponent.GetValue() == True:
            self.cbText1.SetLabel("NA")
            self.cbText2.SetLabel("")
            self.cbText3.SetLabel("")
            self.cbText4.SetLabel("")
            self.clearComboBoxes()
        elif self.rbChemical.GetValue() == True:
            self.cbText1.SetLabel("NA")
            self.cbText2.SetLabel("")
            self.cbText3.SetLabel("")
            self.cbText4.SetLabel("")
            self.clearComboBoxes()

    def onSelection(self, e):
        if self.rbAccount.GetValue() == True:
            prod = self.getComboList("test1")
            self.combo2.Clear()
            self.combo2.Append(prod)
        elif self.rbType.GetValue() == True:
            pass
        elif self.rbComponent.GetValue() == True:
            pass
        elif self.rbChemical.GetValue() == True:
            pass

    def onOpen(self, e):
        print("Opening")

    def onCancel(self, e):
        self.Close()

    def getComboList(self, source):
        # Initialize list.
        lst = []

        # Pull accounts from data
        with open(source + ".csv", newline='') as csvFile:
            fileReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in fileReader:
                lst.append(row)

        # Return just the first row.
        lst = lst[0]
        lst.insert(0, "")
        return lst

    def getCategory(self):
        pass

    def getSubcategory(self):
        pass

    def getProduct(self):
        pass

    def clearComboBoxes(self):
        self.combo1.SetSelection(0)
        self.combo2.SetSelection(0)
        self.combo3.SetSelection(0)
        self.combo4.SetSelection(0)
        self.combo1.Clear()
        self.combo2.Clear()
        self.combo3.Clear()
        self.combo4.Clear()

def main():
    app = wx.App()
    OpenFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
