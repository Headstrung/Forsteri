#=
Data Warehouse Management

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
=#

#= Using Declarations =#
using HDF5

#= Constant Declarations =#
const DATA = "../data/"
const DATABASE = str(DATA, "database.h5")
const REFERENCE = str(DATA, "reference.h5")

#= Outward Functions #=


#= Main Functions =#
function initializeDatabase()
    #=

    =#

    # Open the database file.
    database = h5open(DATABASE, "w")

    # Open the reference file.
    refernece = h5open(REFERENCE, "r")

    # 

end

#= Helper Functions =#

