class OpenFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(OpenFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create main panel.
        self.masterPanel = wx.Panel(self)

        # Create the main box sizer.
        self.masterBox = wx.BoxSizer(orient=wx.VERTICAL)

        # Create sub box sizers.
        self.rbBox = wx.BoxSizer(wx.VERTICAL)
        self.cbBox = wx.BoxSizer(wx.VERTICAL)
        self.rbcbBox = wx.BoxSizer(wx.HORIZONTAL)
        self.bBox = wx.BoxSizer(wx.HORIZONTAL)

        # Create the radio buttons.
        rbText = wx.StaticText(self.masterPanel, label="Search by:")
        rbAccount = wx.RadioButton(self.masterPanel, label="Account", style=wx.RB_GROUP)
        rbType = wx.RadioButton(self.masterPanel, label="Type")
        rbComponent = wx.RadioButton(self.masterPanel, label="Component")
        rbChemical = wx.RadioButton(self.masterPanel, label="Chemical")

        # Add radio buttons to radio button box sizer.
        rbFlag = wx.ALL | wx.ALIGN_LEFT | wx.EXPAND
        self.rbBox.Add(rbText, flag=rbFlag, border=5)
        self.rbBox.Add(rbAccount, flag=rbFlag, border=5)
        self.rbBox.Add(rbType, flag=rbFlag, border=5)
        self.rbBox.Add(rbComponent, flag=rbFlag, border=5)
        self.rbBox.Add(rbChemical, flag=rbFlag, border=5)

        # Create the drop down menus (account is initially selected).
        accounts = self.getAccounts()
        cbText = wx.StaticText(self.masterPanel, label="Select:")
        combo1 = wx.ComboBox(self.masterPanel, choices=accounts, style=wx.CB_READONLY)
        combo1.SetSelection(0)
        combo2 = wx.ComboBox(self.masterPanel, choices=[], style=wx.CB_READONLY)
        combo2.Dismiss()

        # Add combo boxes to combo box box sizer.
        cbFlag = wx.ALL | wx.ALIGN_LEFT | wx.EXPAND
        self.cbBox.Add(cbText, flag=cbFlag, border=5)
        self.cbBox.Add(combo1, flag=cbFlag, border=5)
        self.cbBox.Add(combo2, flag=cbFlag, border=5)

        # Add radio buttons and combo boxes to their box sizer.
        rbcbFlag = wx.ALL | wx.ALIGN_LEFT | wx.EXPAND
        self.rbcbBox.Add(self.rbBox, flag=rbcbFlag, border=10)
        self.rbcbBox.Add((30, -1))
        self.rbcbBox.Add(self.cbBox, flag=rbcbFlag, border=10)

        # Create the open and cancel buttons.
        openButton = wx.Button(self.masterPanel, id=wx.ID_OPEN, label="&Open")
        cancelButton = wx.Button(self.masterPanel, id=wx.ID_CANCEL, label="&Cancel")
        openButton.SetFocus()

        # Add buttons to button box sizer.
        bFlag = wx.ALL | wx.EXPAND | wx.ALIGN_CENTER
        self.bBox.Add((100, -1))
        self.bBox.Add(openButton, flag=bFlag, border=5)
        self.bBox.Add(cancelButton, flag=bFlag, border=5)

        # Add sub box sizer to the main box sizer.
        masterFlag = wx.ALL | wx.EXPAND
        self.masterBox.Add(self.rbcbBox, flag=masterFlag, border=10)
        self.masterBox.Add((-1, 5))
        self.masterBox.Add(self.bBox, flag=masterFlag | wx.ALIGN_CENTER, border=10)

        # Set the sizer for the main panel.
        self.masterPanel.SetSizer(self.masterBox)

        # Bind button presses to functions.
        self.Bind(wx.EVT_RADIOBUTTON, self.onAccount, rbAccount)
        self.Bind(wx.EVT_RADIOBUTTON, self.onType, rbType)
        self.Bind(wx.EVT_RADIOBUTTON, self.onComponent, rbComponent)
        self.Bind(wx.EVT_RADIOBUTTON, self.onChemical, rbChemical)
        self.Bind(wx.EVT_COMBOBOX, self.onAccountSelection, combo1)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelButton)

        # Set window properties.
        self.SetSize((600, 400))
        self.SetTitle("Open Forecast")
        self.Centre()
        self.Show(True)

    def onCancel(self, e):
        self.Close()

    def onAccount(self, e):
        pass
        # Create drop down menus.
        #accountDD = wx.ComboBox(self.masterPanel, choices=accounts, style=wx.CB_READONLY)
        #productDD = wx.ComboBox(self.masterPanel, choices=, style=wx.CB_READONLY)

        #self.ddBox.Add(accountDD, flag=wx.TOP, border=5)

    def onAccountSelection(self, e):
        print("Here")

    def onType(self, e):
        print("Type Selected")

    def onClassSelection(self, e):
        pass

    def onCategorySelection(self, e):
        pass

    def onComponent(self, e):
        print("Component Selected")

    def onChemical(self, e):
        print("Chemical Selected")

    def getAccounts(self):
        # Initialize common variables.
        accounts = []
        source = "account.csv"

        # Pull accounts from data
        with open(source, newline='') as csvFile:
            fileReader = csv.reader(csvFile, delimiter=',', quotechar='|')
            for row in fileReader:
                accounts.append(row)

        # Return just the first row.
        accounts = accounts[0]
        accounts.insert(0, "--")
        return accounts

    def getClasses(self):
        pass

    def getCategory(self):
        pass

    def getSubcategory(self):
        pass

    def getProduct(self):
        pass

class AboutFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AboutFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create html text.
        text = """
          <html>
            <body bgcolor="#43A8ED">
            <center>
              <h1>Forsteri</h1>
              <h5>Version 0.0.1</h5>
              <p>Build for Product Quest Manufacturing LLC</p>
              <p>
                Forsteri is forecasting software that manages high dimentional
                data and impliments statistical learning algorithms with the
                goal of predicting product demand.
              </p>
              <p>Copyright &copy; 2014 Andrew Charles Hawkins</p>
            </center>
          </html>
          """

        # Create the html window.
        html = wx.html.HtmlWindow(self)

        # Check for gtk2 and set the proper font.
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()

        # Set the font to be displayed in the page.
        html.SetPage(text)

        # Set window properties.
        self.SetTitle("About Forsteri")
        self.SetSize((350, 250))
        self.Centre()
        self.Show(True)

class LicenseFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(LicenseFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create text.
        text = """
          This program is free software: you can redistribute it and/or modify
          it under the terms of the GNU General Public License as published by
          the Free Software Foundation, either version 3 of the License, or
          (at your option) any later version.

          This program is distributed in the hope that it will be useful,
          but WITHOUT ANY WARRANTY; without even the implied warranty of
          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
          GNU General Public License for more details.

          You should have received a copy of the GNU General Public License
          along with this program.  If not, see <http://www.gnu.org/licenses/>.
        """

        # Create the static text box.
        staticText = wx.StaticText(self, label=text, style=wx.ALIGN_CENTRE, pos=(20, 20))
        #staticText.SetForegroundColour("red")

        # Create the buttons.
        license = wx.Button(self, label="&License", pos=(58, 240))
        close = wx.Button(self, id=wx.ID_CLOSE, label="&Close", pos=(415, 240))
        close.SetFocus()

        # Bind buttons to functions.
        self.Bind(wx.EVT_BUTTON, self.onShow, license)
        self.Bind(wx.EVT_BUTTON, self.onClose, close)

        # Set window properties.
        self.SetBackgroundColour("#43A8ED")
        self.SetTitle("License Information")
        self.SetSize((565, 330))
        self.Centre()
        self.Show(True)

    def onShow(self, e):
        webbrowser.open("http://www.gnu.org/licenses/gpl.html")

    def onClose(self, e):
        self.Close()
