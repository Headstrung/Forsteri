#!/usr/bin/python

"""
Data Viewer Frame

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
import int_data as idata
import wx
import wx.grid

"""
Constant Declarations
"""


"""
Frame Class
"""
class DataViewer(wx.Frame):
    """
    """

    def __init__(self, product, variable, *args, **kwargs):
        """
        Initialize the frame.

        Args:
          *args (): Any arguments to be passed directly to the super's
            constructor.
          **kwargs (): Any keyword arguments to be passed to the super's
            constructor.

        Returns:
          DataViewer
        """

        ## Initial Operations
        # Get the data.
        data = idata.getData(product, idata.toSQLName(variable))

        ## Frame
        # Initialize by the parent's constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        masterPanel = wx.Panel(self)

        # Create the master sizer.
        masterSizer = wx.BoxSizer(wx.VERTICAL)

        ## Text
        # Create static text boxes.
        productText = wx.StaticText(masterPanel, label=product)
        variableText = wx.StaticText(masterPanel, label=variable[:-8])

        ## Grid
        # Initialize the grid.
        grid = wx.grid.Grid(masterPanel)

        # Create the grid.
        grid.CreateGrid(len(data), 2)

        # Set the column labels.
        grid.SetColLabelValue(0, "Date")
        grid.SetColLabelValue(1, "Value")

        # Populate the grid with data.
        index = 0
        for row in data:
            # Add the data to the grid.
            grid.SetCellValue(index, 0, row[0])
            grid.SetCellValue(index, 1, str(row[1]))

            # Set the date column to be read only.
            grid.SetReadOnly(index, 0)

            # Increment the index.
            index += 1

        # Find the grid width.
        gridWidth = sum([grid.GetColSize(i) for i in range(0, len(data[0]))]) \
            + 115

        ## Frame Operations
        # Add the grid to the master sizer.
        masterSizer.Add(productText, flag=wx.TOP|wx.ALIGN_CENTER, border=10)
        masterSizer.Add(variableText, flag=wx.BOTTOM|wx.ALIGN_CENTER, border=5)
        masterSizer.Add(grid, flag=wx.ALL|wx.EXPAND, border=5)

        # Set the sizer for the master panel.
        masterPanel.SetSizer(masterSizer)

        # Set window properties.
        self.SetSize((gridWidth, 565))
        self.SetTitle("Data Viewer")
        self.Centre()
        self.Show(True)

    def populate(data):
        """
        """

        # 
        pass

def main():
    """
    """

    app = wx.App()
    DataViewer("CVS-B3RH1-00", "Finished Goods", None)
    app.MainLoop()

if __name__ == '__main__':
    main()
