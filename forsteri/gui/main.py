"""
Main Frame

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

# Import python modules.
import os
import subprocess as sp
import threading as td
import webbrowser as wb
import wx

# Import forsteri modules.
from forsteri.gui.window import assign_missing as am
from forsteri.gui.window import data_manager as dm
from forsteri.gui.window import import_data as imd
from forsteri.gui.window import link_products as lp
from forsteri.gui.window import new_item as nif
from forsteri.gui.window import open_product as omp
from forsteri.gui.window import preferences as pref
from forsteri.gui.window import product as pr
from forsteri.interface import data as idata
from forsteri.process import model as pm

class Main(wx.Frame):
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
        super(Main, self).__init__(*args, **kwargs)

        # Create the master panel.
        self.masterPanel = pr.ProductPanel(self)

        # Create the icon.
        self.icon = wx.Icon(os.path.join(idata.DATA, "Forsteri", "img",
            "forsteri.ico"), wx.BITMAP_TYPE_ICO)

        ## Frame Operations
        # Set the menu bar
        self.SetMenuBar(self.create_menu_bar())

        # Set the icon.
        self.SetIcon(self.icon)

        # Set window properties.
        self.SetSize((1030, 585))
        self.SetTitle("Forsteri")
        self.Centre()
        self.Show(True)

    def create_menu_bar(self):
        """
        Create the manu bar.

        Args:
          None

        Returns:
          wx.MenuBar
        """

        # Create the menu bar.
        menuBar = wx.MenuBar()

        # Create the file menu.
        fileMenu = wx.Menu()

        # Create the file menu items.
        openProducts = wx.MenuItem(fileMenu, wx.ID_OPEN,
            "&Open/Manage Products")
        newForecast = wx.MenuItem(fileMenu, wx.ID_NEW, "&New Item Forecast")
        importData = wx.MenuItem(fileMenu, wx.ID_ADD, "&Import Data")
        quit = wx.MenuItem(fileMenu, wx.ID_EXIT)

        # Create the utilities submenu in file menu.
        utilities = wx.Menu()

        # Create the utilities menu items.
        assignMissing = wx.MenuItem(utilities, wx.ID_JUMP_TO,
            "&Assign Missing")
        linkProducts = wx.MenuItem(utilities, wx.ID_CONVERT, "&Link Products")
        systematizeDB = wx.MenuItem(utilities, wx.ID_SORT_ASCENDING,
            "&Systematize Database")
        runModels = wx.MenuItem(utilities, wx.ID_EXECUTE, "&Run Models")
        updateErrors = wx.MenuItem(utilities, wx.ID_UP, "&Update Errors")

        # Bind the utilities menu items to actions.
        self.Bind(wx.EVT_MENU, self.on_assign, assignMissing)
        self.Bind(wx.EVT_MENU, self.on_link, linkProducts)
        self.Bind(wx.EVT_MENU, self.on_systematize, systematizeDB)
        self.Bind(wx.EVT_MENU, self.on_model, runModels)
        self.Bind(wx.EVT_MENU, self.on_update, updateErrors)

        # Add the items to the utilities menu.
        utilities.AppendItem(assignMissing)
        utilities.AppendItem(linkProducts)
        utilities.AppendSeparator()
        utilities.AppendItem(systematizeDB)
        utilities.AppendItem(runModels)
        utilities.AppendItem(updateErrors)

        # Bind the file menu items to actions.
        self.Bind(wx.EVT_MENU, self.on_open, openProducts)
        self.Bind(wx.EVT_MENU, self.on_new_forecast, newForecast)
        self.Bind(wx.EVT_MENU, self.on_import, importData)
        self.Bind(wx.EVT_MENU, self.on_quit, quit)

        # Add the items to the file menu.
        fileMenu.AppendItem(openProducts)
        fileMenu.AppendItem(newForecast)
        fileMenu.AppendItem(importData)
        fileMenu.AppendSeparator()
        fileMenu.AppendSubMenu(utilities, "&Utilities")
        fileMenu.AppendSeparator()
        fileMenu.AppendItem(quit)

        # Create the edit menu.
        editMenu = wx.Menu()

        # Create the edit menu items.
        dataManager = wx.MenuItem(editMenu, wx.ID_REFRESH,
            "&Data Manager...")
        connections = wx.MenuItem(editMenu, wx.ID_NETWORK, "&Connections")
        preferences = wx.MenuItem(editMenu, wx.ID_PREFERENCES)

        # Bind the edit menu items to actions.
        self.Bind(wx.EVT_MENU, self.on_data_manager, dataManager)
        self.Bind(wx.EVT_MENU, self.on_connection, connections)
        self.Bind(wx.EVT_MENU, self.on_preferences, preferences)

        # Add the items to the edit menu.
        editMenu.AppendItem(dataManager)
        editMenu.AppendSeparator()
        editMenu.AppendItem(connections)
        editMenu.AppendItem(preferences)

        # Create the help menu.
        helpMenu = wx.Menu()

        # Create the help menu items.
        documentation = wx.MenuItem(helpMenu, wx.ID_INDEX, "&Documentation")
        titleHelp = wx.MenuItem(helpMenu, wx.ID_HELP)
        about = wx.MenuItem(helpMenu, wx.ID_ABOUT)

        # Bind the help menu items to actions.
        self.Bind(wx.EVT_MENU, self.on_documentation, documentation)
        self.Bind(wx.EVT_MENU, self.on_help, titleHelp)
        self.Bind(wx.EVT_MENU, self.on_about, about)

        # Add the items to the help menu.
        helpMenu.AppendItem(documentation)
        helpMenu.AppendItem(titleHelp)
        helpMenu.AppendSeparator()
        helpMenu.AppendItem(about)

        # Add the items to the menu bar.
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")

        return menuBar

    def on_open(self, event):
        """
        What to do when the open menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the open menu
            item is selected.

        Returns:
          None
        """

        # Create the open product dialog.
        openProd = omp.OpenDialog(self,
            style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

        # Show the open product dialog.
        returnID = openProd.ShowModal()

        # If the returned value is cancel, do nothind. If the returned value is
        # open, set the product in the product panel.
        if returnID == wx.ID_OPEN:
            # Get the selected products.
            products = openProd.getSelection()

            # If only one product is selected, set the product, otherwise, do
            # nothing.
            if len(products) == 1:
                self.masterPanel.setProduct(products[0])

        # Destroy the open product dialog.
        openProd.Destroy()

    def on_new_forecast(self, event):
        """
        """

        # Create the new item forecast frame.
        nif.NewItemFrame(self, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

    def on_import(self, event):
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

    def on_assign(self, event):
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

    def on_link(self, event):
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

    def on_systematize(self, event):
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

    def on_model(self, event):
        """
        """

        # Run the models.
        modelThread = td.Thread(target=pm.runAll)
        modelThread.start()

    def on_update(self, event):
        """
        """

        # Create the update error threads.
        updateThread = td.Thread(target=pm.runAllErrors)
        updateThread.start()

    def on_quit(self, event):
        """
        What to do when the quit menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the quit menu
            item is selected.

        Returns:
          None
        """

        self.Close()

    def on_data_manager(self, event):
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

    def on_connection(self, event):
        """
        What to do when the connection menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the
            connection menu item is selected.

        Returns:
          None
        """

        pass

    def on_preferences(self, event):
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

    def on_documentation(self, event):
        """
        What to do when the documentation menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the
            documentation menu item is selected.

        Returns:
          None
        """

        wb.open("http://achawkins.github.io/Forsteri", new=2)

    def on_help(self, event):
        """
        What to do when the help menu item has been selected.

        Args:
          event(wx._core.CommandEvent): The triggered event when the help menu
            item is selected.

        Returns:
          None
        """

        wb.open("mailto:andrewh@pqmfg.com")

    def on_about(self, event):
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
        license = """The MIT License (MIT)

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
THE SOFTWARE."""

        # Create and set the dialog information.
        info = wx.AboutDialogInfo()
        info.SetName("Forsteri")
        info.SetVersion("0.0.1")
        info.SetDescription(description)
        info.SetWebSite("http://github.com/Headstrung/forsteri")
        info.SetCopyright("Copyright (C) 2014, 2015 Andrew Hawkins")
        info.SetLicense(license)
        info.AddDeveloper("Andrew Hawkins <andrewh@pqmfg.com>")
        info.AddDocWriter("Andrew Hawkins <andrewh@pqmfg.com>")

        # Make the diolog box.
        wx.AboutBox(info)

if __name__ == '__main__':
    app = wx.App()
    Main(None, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)
    app.MainLoop()
