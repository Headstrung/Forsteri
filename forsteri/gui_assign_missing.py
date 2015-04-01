#!/usr/bin/python

"""
Assign Missing Items Frame

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
import wx

"""
Contant Declarations
"""


"""
Frame Class
"""
class AssignFrame(wx.Frame):
    """
    """

    def __init__(self, *args, **kwargs):
        """
        """

        ## Frame
        # Initialize the parents constructor.
        super().__init__(*args, **kwargs)

        # Create the master panel.
        self.masterPanel = pr.ProductPanel(self)

        # 
        
