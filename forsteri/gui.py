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
import gui_assign_missing as am
import gui_data_manager as dm
import gui_import_data as imd
import gui_link_products as lp
import gui_new_item as nif
import gui_open_product as omp
import gui_preferences as pref
import gui_product as pr
import int_data as idata
import pro_model as pm
import subprocess as sp
import threading as td
import webbrowser as wb
import wx
import wx.adv

"""
Constant Declarations
"""
TITLE = "Forsteri"

"""
Frame Class
"""
class MainFrame(wx.Frame):
    """
    A frame that contains the menu and status bars as well as opened product's
    information. This frame is created on start up and is the main frame for
    the application. All subsequent interaction with the application with be
    through this frame.

    Extends:
      wx.Frame
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the frame.

        Args:
          *args (tuple of object): Any arguments to be passed directly to the
            super's constructor.
          **kwargs (dictionary of name: object): Any keyword arguments to be
            passed to the super's constructor.

        Returns:
          MainFrame

        To Do:

        """

        ## Frame
        # Initialize the parents constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        self.masterPanel = pr.ProductPanel(self)

        ## Status Bar
        # Create and initlialize the status bar.
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetStatusText("Ready")

        ## Frame Operations
        # Set the menu bar
        self.SetMenuBar(self.createMenuBar())

        # Set window properties.
        self.SetSize((1050, 600))
        self.SetTitle(TITLE)
        self.Centre()
        self.Show(True)

    """
    Helper Functions
    """
    def createMenuBar(self):
        """
        Create the manu bar.

        Args:
          None

        Returns:
          wx.MenuBar
        """

        ## File
        # Create the File menu..
        fileMenu = wx.Menu()

        # Create the File menu items.
        openProducts = wx.MenuItem(fileMenu, wx.ID_OPEN,
            "&Open/Manage Products")
        newForecast = wx.MenuItem(fileMenu, wx.ID_NEW, "&New Item Forecast")
        importData = wx.MenuItem(fileMenu, wx.ID_ADD, "&Import Data")
        utilities = wx.Menu()
        quit = wx.MenuItem(fileMenu, wx.ID_EXIT)

        # Create the Utilitites sub menu items.
        assignMissing = wx.MenuItem(utilities, wx.ID_JUMP_TO,
            "&Assign Missing")
        linkProducts = wx.MenuItem(utilities, wx.ID_CONVERT, "&Link Products")
        systematizeDB = wx.MenuItem(utilities, wx.ID_UP,
            "&Systematize Database")
        runModels = wx.MenuItem(utilities, wx.ID_EXECUTE, "&Run Models")

        # Add items to the Utilities sub menu.
        utilities.Append(assignMissing)
        utilities.Append(linkProducts)
        utilities.AppendSeparator()
        utilities.Append(systematizeDB)
        utilities.Append(runModels)

        # Add items to the File menu.
        fileMenu.Append(openProducts)
        fileMenu.Append(newForecast)
        fileMenu.Append(importData)
        fileMenu.AppendSeparator()
        fileMenu.AppendSubMenu(utilities, "&Utilities")
        fileMenu.AppendSeparator()
        fileMenu.Append(quit)

        # Edit
        # Create the Edit menu.
        editMenu = wx.Menu()

        # Create the Edit menu items.
        dataManager = wx.MenuItem(editMenu, wx.ID_REFRESH,
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
        self.Bind(wx.EVT_MENU, self.onNewForecast, newForecast)
        self.Bind(wx.EVT_MENU, self.onImport, importData)
        self.Bind(wx.EVT_MENU, self.onAssign, assignMissing)
        self.Bind(wx.EVT_MENU, self.onLink, linkProducts)
        self.Bind(wx.EVT_MENU, self.onSystematize, systematizeDB)
        self.Bind(wx.EVT_MENU, self.onModel, runModels)
        self.Bind(wx.EVT_MENU, self.onQuit, quit)
        self.Bind(wx.EVT_MENU, self.onDataManager, dataManager)
        self.Bind(wx.EVT_MENU, self.onConn, connections)
        self.Bind(wx.EVT_MENU, self.onPref, preferences)
        self.Bind(wx.EVT_MENU, self.onDoc, documentation)
        self.Bind(wx.EVT_MENU, self.onHelp, titleHelp)
        self.Bind(wx.EVT_MENU, self.onAbout, about)

        # Return menu bar.
        return menuBar

    """
    Event Handler Functions
    """
    def onOpen(self, event):
        """
        What to do when the open menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the open menu
            item is selected.

        Returns:
          None
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
            if len(products) == 1:
                self.masterPanel.setProduct(products[0])
        elif returnID == wx.ID_PRINT:
            pass

        # Destroy the open/manage products dialog.
        openProd.Destroy()

    def onNewForecast(self, event):
        """
        """

        # Create the new item forecast frame.
        nif.NewItemFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onImport(self, event):
        """
        What to do when the import menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the import
            menu item is selected.

        Returns:
          None
        """

        # Create the import data frame.
        imd.ImportFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onAssign(self, event):
        """
        What to do when the assign missing menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the assign
            missing menu item is selected.

        Returns:
          None
        """

        # Create the assign missing frame.
        am.AssignFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onLink(self, event):
        """
        What to do when the link menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the link menu
            item is selected.

        Returns:
          None
        """

        # Create the link products frame.
        lp.LinkFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onSystematize(self, event):
        """
        What to do when the sync menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the sync menu
            item is selected.

        Returns:
          None
        """

        # Systematize the database.
        systematizeThread = td.Thread(target=idata.systematize)
        systematizeThread.start()

    def onModel(self, event):
        """
        """

        # Create and run the EMA model thread.
        #eMAThread = td.Thread(target=pm.runEMA)
        #eMAThread.start()

        # Create and run the MLR model thread.
        mLRThread = td.Thread(target=pm.runMLR)
        mLRThread.start()

    def onQuit(self, event):
        """
        What to do when the quit menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the quit menu
            item is selected.

        Returns:
          None
        """

        self.Close()

    def onDataManager(self, event):
        """
        What to do when the data manager menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the data
            manager menu item is selected.

        Returns:
          None
        """

        # Create the data manager frame.
        dm.ManagerFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onConn(self, event):
        """
        What to do when the connection menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the
            connection menu item is selected.

        Returns:
          None
        """

        pass

    def onPref(self, event):
        """
        What to do when the preferences menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the
            preferences menu item is selected.

        Returns:
          None
        """

        pref.PreferencesFrame(self,
            style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def onDoc(self, event):
        """
        What to do when the documentation menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the
            documentation menu item is selected.

        Returns:
          None
        """

        sp.Popen("../doc/Forsteri.pdf", shell=True)

    def onHelp(self, event):
        """
        What to do when the help menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the help menu
            item is selected.

        Returns:
          None
        """

        wb.open("mailto:andrewh@pqmfg.com")

    def onAbout(self, event):
        """
        What to do when the about menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the about menu
            item is selected.

        Returns:
          None
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
        info.SetName(TITLE)
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
    When the file is called independently create and display the main frame.
    """

    # Create the application.
    app = wx.App()

    # Create the bitmap used for the splash screen.
    bitmap = wx.Bitmap("/home/andrew/Dropbox/product-quest/Forsteri/data/" +\
        "img/logo.png", wx.BITMAP_TYPE_PNG)

    # Create the splash screen.
    splash = wx.adv.SplashScreen(bitmap,
        wx.adv.SPLASH_CENTRE_ON_SCREEN|wx.adv.SPLASH_TIMEOUT, 1000, None)

    # Create the main frame.
    MainFrame(None, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    # Start the application main loop.
    app.MainLoop()

if __name__ == '__main__':
    main()
