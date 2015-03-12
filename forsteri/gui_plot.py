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
import numpy as np
import matplotlib
matplotlib.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

import wx

class CanvasPanel(wx.Panel):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        #
        wx.Panel.__init__(self, *args, **kwargs)

        self.figure = Figure()
        self.axis = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.RIGHT|wx.BOTTOM|wx.GROW,
            border=5)
        self.SetSizer(sizer)
        self.Fit()

    def draw(self):
        """
        """

        t = np.arange(-3, 3, 0.01)
        s = np.exp(-t ** 2)
        self.axis.plot(t, s)

if __name__ == "__main__":
    app = wx.App()
    fr = wx.Frame(None, title="I Win")
    panel = CanvasPanel(fr)
    panel.draw()
    fr.Show()
    app.MainLoop()
