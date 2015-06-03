"""
Data Viewer Frame

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
import wx
import wx.grid

from forsteri.interface import data as idata

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
        super(DataViewer, self).__init__(*args, **kwargs)

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
            + 130

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
