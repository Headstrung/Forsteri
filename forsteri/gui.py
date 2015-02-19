#!/usr/bin/python

"""
Graphical User Interface

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
import csv
import gui_data_manager as dm
import gui_import_data as imd
import gui_open_product as omp
import int_hdf5 as ihdf5
import subprocess as sp
import webbrowser as wb
import wx
import wx.html
import wx.adv

"""
Frame Class
"""
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        """
        """

        ## Frame
        # Initialize the parents constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.GridBagSizer(5, 5)

        # Get the data for the default product (this will be a get method).
        title = "ACT-ABCDE-00"
        account = "Account"
        tier = "Class - Category - Subcategory"
        desc = """The red fox jumped over the moon with a spoon and landed
 on his broom."""
        forecast = [100, 200, 800, 1200, 700, 900, 1400, 2500, 100, 200,
            300, 200]
        previous1 = [100, 200, 800, 1200, 700, 900, 1400, 2500, 100, 200,
            300, 200]
        previous2 = [100, 200, 800, 1200, 700, 900, 1400, 2500, 100, 200,
            300, 200]

        ## Title
        # Create the title sizer.
        titleSizer = wx.BoxSizer(wx.VERTICAL)

        # Create font styles.
        titleFont = wx.Font(30, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        subFont = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL)

        # Create the static text.
        self.titleText = wx.StaticText(masterPanel, label=title)
        self.titleText.SetFont(titleFont)
        self.accountText = wx.StaticText(masterPanel, label=account)
        self.accountText.SetFont(subFont)
        self.tierText = wx.StaticText(masterPanel, label=tier)
        self.tierText.SetFont(subFont)

        # Add the static text to the sizer.
        titleSizer.Add(self.titleText)
        titleSizer.Add(self.accountText)
        titleSizer.Add(self.tierText)

        ## Menu Bar
        # Create the menu bar.
        menuBar = self.createMenuBar()

        ## Status Bar
        # Create and initlialize the status bar.
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetStatusText("Ready")

        ## Frame Operations
        # Set the menu bar
        self.SetMenuBar(menuBar)

        # Add everything to the master sizer.
        masterSizer.Add(titleSizer, pos=(0,0), span=(3, 5),
            flag=wx.ALIGN_CENTER|wx.EXPAND)

        #masterSizer.AddGrowableCol(0)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((1000, 625))
        self.SetTitle("Forsteri")
        self.Centre()
        self.Show(True)

    """
    Helper Functions
    """
    def createMenuBar(self):
        """
        """

        ## File
        # Create the File menu..
        fileMenu = wx.Menu()

        # Create the File menu items.
        openProducts = wx.MenuItem(fileMenu, wx.ID_OPEN,
            "&Open/Manage Products")
        importData = wx.MenuItem(fileMenu, wx.ID_ADD, "&Import Data")
        utilities = wx.Menu()
        quit = wx.MenuItem(fileMenu, wx.ID_EXIT)

        # Create the Utilitites sub menu items.
        linkProds = wx.MenuItem(utilities, wx.ID_CONVERT, "&Link Products")
        syncDB = wx.MenuItem(utilities, wx.ID_UP, "&Sync Database")
        shrinkHDF = wx.MenuItem(utilities, wx.ID_ZOOM_OUT, "&Shrink HDF5 File")

        # Add items to the Utilities sub menu.
        utilities.Append(linkProds)
        utilities.AppendSeparator()
        utilities.Append(syncDB)
        utilities.Append(shrinkHDF)

        # Add items to the File menu.
        fileMenu.Append(openProducts)
        fileMenu.Append(importData)
        fileMenu.AppendSeparator()
        fileMenu.AppendSubMenu(utilities, "&Utilities")
        fileMenu.AppendSeparator()
        fileMenu.Append(quit)

        # Edit
        # Create the Edit menu.
        editMenu = wx.Menu()

        # Create the Edit menu items.
        dataManager = wx.MenuItem(editMenu, wx.ID_EXECUTE,
            "&Data Manager...")
        connections = wx.MenuItem(editMenu, wx.ID_NETWORK, "&Connections")
        preferences = wx.MenuItem(editMenu, wx.ID_PREFERENCES)

        # Add items to the Edit menu.
        editMenu.Append(dataManager)
        editMenu.AppendSeparator()
        editMenu.Append(connections)
        editMenu.Append(preferences)

        ## Help
        # Create the Help menu.
        helpMenu = wx.Menu()

        # Create the Help menu items.
        documentation = wx.MenuItem(helpMenu, wx.ID_INDEX, "&Documentation")
        titleHelp = wx.MenuItem(helpMenu, wx.ID_HELP)
        about = wx.MenuItem(helpMenu, wx.ID_ABOUT)

        # Add items to the Help menu.
        helpMenu.Append(documentation)
        helpMenu.Append(titleHelp)
        helpMenu.AppendSeparator()
        helpMenu.Append(about)

        ## Menu Bar Operations
        # Create Menu Bar and add contents.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")

        # Bind selections to functions.
        self.Bind(wx.EVT_MENU, self.onOpen, openProducts)
        self.Bind(wx.EVT_MENU, self.onImport, importData)
        self.Bind(wx.EVT_MENU, self.onShrinkHDF, shrinkHDF)
        self.Bind(wx.EVT_MENU, self.onDataManager, dataManager)
        self.Bind(wx.EVT_MENU, self.onDoc, documentation)
        self.Bind(wx.EVT_MENU, self.onHelp, titleHelp)
        self.Bind(wx.EVT_MENU, self.onQuit, quit)
        self.Bind(wx.EVT_MENU, self.onAbout, about)

        # Return menu bar.
        return menuBar

    """
    Event Handler Functions
    """
    def onOpen(self, event):
        """
        """

        # Create the open/manage products dialog.
        openProd = omp.OpenDialog(self,
            style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

        # Show the open/manage products dialog.
        returnID = openProd.ShowModal()

        # If cancel was selected return.
        if returnID == wx.ID_CANCEL:
            return

        # Get a list of the products that were selected.
        products = openProd.getSelection()

        # Perform necessary operations after returning.
        if returnID == wx.ID_OPEN:
            print("Open")
        elif returnID == wx.ID_PRINT:
            print("Report")

        # Destroy the open/manage products dialog.
        openProd.Destroy()

    def onImport(self, event):
        """
        """

        # Create the import data frame.
        imd.ImportFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onShrinkHDF(self, event):
        """
        """

        # Repack the database.
        ihdf5.repackDB()

    def onQuit(self, event):
        """
        """

        self.Close()

    def onDataManager(self, event):
        """
        """

        # Create the data manager frame.
        dm.ManagerFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onDoc(self, event):
        """
        """

        sp.Popen("../doc/Forsteri.pdf", shell=True)

    def onHelp(self, event):
        """
        """

        wb.open("mailto:andrewh@pqmfg.com")

    def onAbout(self, event):
        """
        """

        # Create the description and license text.
        description = "Forsteri is forecasting software that manages high " +\
        "dimentional data and impliments statistical learning algorithms " +\
        "with the goal of predicting product demand."
        license = """Forsteri is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

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
        info.SetCopyright("Copyright (C) 2014, 2015 Andrew Hawkins")
        info.SetLicense(license)
        info.AddDeveloper("Andrew Hawkins <andrewh@pqmfg.com>")
        info.AddDocWriter("Andrew Hawkins <andrewh@pqmfg.com>")

        # Make the diolog box.
        wx.adv.AboutBox(info)

def main():
    """
    """

    # Create the application.
    app = wx.App()

    # Create the bitmap used for the splash screen.
    bitmap = wx.Bitmap("/home/andrew/Dropbox/product-quest/Forsteri/data/" +\
        "logo.png", wx.BITMAP_TYPE_PNG)

    # Create the splash screen.
    splash = wx.adv.SplashScreen(bitmap,
        wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT, 20, None)

    # Create the main frame.
    MainFrame(None)

    # Start the application main loop.
    app.MainLoop()

if __name__ == '__main__':
    main()
