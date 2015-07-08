"""
Forsteri Client

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

import os
import sys
import wx

from forsteri import gui

class ForsteriClient(object):
    """
    """

    def __init__(self, username, path):

        self.USERNAME = username
        self.PATH = path

    def run(self):
        # Create the application.
        app = wx.App()

        # Check if the splash screen flag was given.
        if "-s" in sys.argv:
            # Create the bitmap used for the splash screen.
            here = os.path.abspath(os.path.dirname(__file__))
            bitmap = wx.Bitmap(os.path.join(here, "..", "data", "img",
                "logo.png"), wx.BITMAP_TYPE_PNG)

            # Create the splash screen.
            splash = wx.SplashScreen(bitmap,
                wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 1000, None)

        # Create the main frame.
        gui.Main(None, style=wx.DEFAULT_FRAME_STYLE^wx.RESIZE_BORDER)

        # Start the application main loop.
        app.MainLoop()

if __name__ == "__main__":
    CLIENT = ForsteriClient()
    CLIENT.run()
