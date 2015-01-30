#!/usr/bin/python

"""
Graphical User Interface

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
import subprocess
import webbrowser
import wx
import wx.html
import wx.adv

""" Frame CLass """
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # Create and set the menu bar.
        menuBar = self.createMenuBar()
        self.SetMenuBar(menuBar)

        # Create and initlialize status bar.
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetStatusText("Ready")

        # Set window properties.
        #self.SetBackgroundColour("#2A211C")
        self.SetSize((800, 500))
        self.SetTitle("Forsteri")
        self.Centre()
        self.Show(True)

    def createMenuBar(self):
        # Create File menu and contents.
        fileMenu = wx.Menu()
        openForecast = wx.MenuItem(fileMenu, wx.ID_OPEN, "&Open Forecast")
        fileMenu.Append(openForecast)
        importData = wx.MenuItem(fileMenu, wx.ID_ADD, "&Import Data")
        fileMenu.Append(importData)
        fileMenu.AppendSeparator()
        quit = wx.MenuItem(fileMenu, wx.ID_EXIT)
        fileMenu.Append(quit)

        # Create Edit meu and contents.
        editMenu = wx.Menu()
        productManager = wx.MenuItem(editMenu, wx.ID_EXECUTE,
            "&Data Manager...")
        editMenu.Append(productManager)

        # Create Help menu and contents.
        helpMenu = wx.Menu()
        documentation = wx.MenuItem(helpMenu, wx.ID_INDEX, "&Documentation")
        helpMenu.Append(documentation)
        titleHelp = wx.MenuItem(helpMenu, wx.ID_HELP)
        helpMenu.Append(titleHelp)
        helpMenu.AppendSeparator()
        #licenseInformation = wx.MenuItem(helpMenu, wx.ID_ANY, "&License Information...")
        #helpMenu.Append(licenseInformation)
        about = wx.MenuItem(helpMenu, wx.ID_ABOUT)
        helpMenu.Append(about)

        # Create Menu Bar and add contents.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")

        # Bind selections to functions.
        self.Bind(wx.EVT_MENU, self.onOpen, openForecast)
        self.Bind(wx.EVT_MENU, self.onDoc, documentation)
        self.Bind(wx.EVT_MENU, self.onHelp, titleHelp)
        self.Bind(wx.EVT_MENU, self.onQuit, quit)
        self.Bind(wx.EVT_MENU, self.onAbout, about)
        #self.Bind(wx.EVT_MENU, self.onLicense, licenseInformation)

        # Return menu bar.
        return menuBar

    def onOpen(self, e):
        OpenFrame(self)

    def onQuit(self, e):
        self.Close()

    def onDoc(self, e):
        subprocess.Popen("../doc/Forsteri.pdf", shell=True)

    def onHelp(self, e):
        webbrowser.open("mailto:andrewh@pqmfg.com")

    # Depricated
    def onLicense(self, e):
        LicenseFrame(self, style=wx.SYSTEM_MENU | wx.CLOSE_BOX)

    def onAbout(self, e):
        #AboutFrame(self, style=wx.SYSTEM_MENU | wx.CLOSE_BOX)

        # Create the description and license text.
        description = """Forsteri is forecasting software that manages high dimentional data and impliments statistical learning algorithms with the goal of predicting product demand."""
        license = """Forsteri is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Forsteri is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Forsteri.  If not, write to:

Free Software Foundation, Inc.
59 Temple Place, Suite 330
Boston, MA  02111-1307  USA"""

        # Create and set the dialog information.
        info = wx.adv.AboutDialogInfo()
        info.SetName("Forsteri")
        info.SetVersion("0.0.1")
        info.SetDescription(description)
        info.SetWebSite("http://github.com/Headstrung/forsteri")
        info.SetCopyright("Copyright (C) 2014 Andrew Hawkins")
        info.SetLicense(license)
        info.AddDeveloper("Andrew Hawkins <andrewh@pqmfg.com>")
        info.AddDocWriter("Andrew Hawkins <andrewh@pqmfg.com>")

        # Make the diolog box.
        wx.adv.AboutBox(info)

def main():
    app = wx.App()
    MainFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
