#module Database
#=
Database

This module contains the algorithms used for reading from and writing to the
HDF5 database file.

Needs:
  Dates
  HDF5

Examples:
  record("CVS-B3RH1-00", "finished-goods", [1.7, 7.9, 4.3], [Date(2014, 9, 1),
    Date(2014, 10, 1), Date(2014, 11, 1)], true)

To Do:
  
=#

using Dates
using HDF5

const BASE_SOURCE = "../data/base.h5"
const DATABASE_SOURCE = "../data/database.h5"

############################################################## Create Functions

function closeDB(database::HDF5File)
    #=
    Close the database.

    Args:
      database (HDF5File): The open database file.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Close the database file.
    close(database)

    # Return successful.
    return true
end

function initializeDB()
    #=
    Initialize a database file.

    Args:
      None

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if a database file is already initialized. If it is, save the old.
    if isfile(DATABASE_SOURCE)
        # Make sure the user wants to initialize the database.
        println("Initializing the database will overwrite the contents of the current database. Do you want to continue? (Y/n)")
        answer = readline(STDIN)
        if lowercase(answer) in ["n\n", "no\n"]
            return false
        end

        # Move the previous database to a new file just in case.
        @linux_only run(`mv ../data/database.h5 ../data/database-old.h5`)
        @windows_only run(`move ..\data\databse.h5 ..\data\database-old.h5`)
    end

    # Open the database file and base file.
    database = h5open(DATABASE_SOURCE, "w")
    base = h5open(BASE_SOURCE, "r")

    # Read in the initialization data.
    products = read(base["prods"])
    skus = read(base["skus"])

    # Close the base file.
    close(base)

    # Add each base product group.
    productsLength = length(products)
    for i = 1 : productsLength
        addProduct(database, products[i])
    end

    # Set the sku attribute for all base product groups.
    addSkus(database, hcat(products, skus))

    # Close the databese file.
    close(database)

    # Return successful.
    return true
end

function openDB()
    #=
    Open the database.

    Args:
      None

    Returns:
      HDF5File: The database.
    =#

    # Open and return the database file.
    return h5open(DATABASE_SOURCE, "r+")
end

function refreshDB(database::HDF5File)
    #=
    Refresh the database in memory.

    Args:
      database (HDF5File): The database to be refreshed.

    Returns:
    HDF5File: The refreshed database.
    =#

    # Close the database file.
    close(database)

    # Reopen and return the database file.
    return h5open(DATABASE_SOURCE, "r+")
end

########################################################## Manipulate Functions

function addProduct(database::HDF5File, product::ASCIIString, attributes::Dict{Any,Any}=Dict(["sku"], -1))
    #=
    Add a product group to the database. (High Frequency)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group to be added to the database.
      attributes (Dict{Any,Any}, optional): Any attributes to associate with
        the product.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if the product group is already defined in the database.
    if has(database, product)
        return false
    end

    # Create the new product group.
    g_create(database, product)

    # Add the attributes, if given.
    for (attribute, value) in attributes
        setAttribute(database, product, attribute, value)
    end

    # Return successful
    return true
end

function addSkus(database::HDF5File, codeSku::Array{Any,2})
    #=
    Add the skus attribute to multiple product groups.

    Args:
      database (HDF5File): The HDF5 database file.
      codeSku (Array{Any,2}): An array matching the product codes (string in
        column 1) to the skus (integer in column 2).

    Retruns:
      Bool: True if successful, false otherwise.
    =#

    # Loop through the rows of the input array and set the 'sku' attribute to
    # be the corresponding value.
    rows = size(codeSku)[1]
    for i = 1 : rows
        setAttribute(database, convert(ASCIIString, codeSku[i, 1]), "sku", int(codeSku[i, 2]))
    end

    # Return successful.
    return true
end

function addVariableToList(variable::ASCIIString)
    #=
    Add a variable to the list of variables held in a database.

    Args:
      base (HDF5File): The HDF5 base file.
      variable (ASCIIString): The variable to add to the list.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Open the base file.
    base = h5open(BASE_SOURCE, "r+")

    # Get the previous list of variables
    variables = read(base["vars"])

    # Add the new variable to the list and resort.
    variables = sort(vcat(variables, variable))

    # Remove the old variable list from the database.
    o_delete(base, "vars")

    # Write the new variable list to the database.
    base["vars"] = variables

    # Close the base file.
    closeDB(base)

    # Return successful.
    return true
end

function getBasisHash()
    #=
    Generate a hash table of skus to codes.

    Args:
      None

    Returns:
      Dict{Int64,ASCIIString}: The hash table to convert skus to codes.
    =#

    # Open the database.
    database = openDB()

    # Initialize variables.
    products = names(database)
    table = (Int64 => ASCIIString)[]

    # For each product, get the corresponding sku from the database.
    for product in products
        table[read(attrs(database[product])["sku"])] = product
    end

    # Close the database.
    closeDB(database)

    # Return the hash table.
    return table
end

function getProductList()
    #=
    Get a list of the currently assigned product groups.

    Args:
      None

    Returns:
      Array{ASCIIString}: The currently assigned product groups.
    =#

    # Open the database.
    database = openDB()

    # Extract the names of the product groups.
    products = names(database)

    # Close the database.
    closeDB(database)

    # Return the hash table.
    return products
end

function getVariable(database::HDF5File, product::ASCIIString, variable::ASCIIString)
    #=
    Get the variable data. (High Frequency)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group the variable dataset will be
        pulled from.
      variable (ASCIIString): The variable title to pull from the product
        group.

    Returns:
      Array{Float64,1}: The variable dataset pulled from the product group.
    =#

    # Check if the product and variable exist.
    if !has(database, product) || !has(database[product], variable)
        return []
    end

    # Return the variable dataset.
    return read(database[product][variable])
end

function getVariableList()
    #=
    Get a list of possible variable assignments.

    Args:
      None

    Returns:
      Array{ASCIIString,1}: The list of variables.
    =#

    # Open the database.
    base = h5open(BASE_SOURCE, "r")

    # Extract the names of the defined variables.
    variableList = read(base["vars"])

    # Close the database.
    closeDB(base)

    # Return the list of variables.
    return variableList
end

function removeAttribute(database::HDF5File, product::ASCIIString, attribute::ASCIIString)
    #=
    Remove an attribute from a product group. (High Frequency)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group the attribute will be removed
        from.
      attribute (ASCIIString): The title of the attribute to remove.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if the attribute is defined in the product group.
    if !exists(attrs(database[product]), attribute)
        return false
    end

    # Delete the attribute.
    a_delete(database[product], attribute)

    # Return successful.
    return true
end

function removeProduct(database::HDF5File, product::ASCIIString)
    #=
    Remove a product group from the database. (High Frequency?)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group to be removed from the database.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if the product group is defined in the database.
    if !has(database, product)
        return false
    end

    # Delete the product group.
    o_delete(database, product)

    # Return successful.
    return true
end

function removeVariable(database::HDF5File, product::ASCIIString, variable::ASCIIString)
    #=
    Remove a variable dataset from a product group. (High Frequency?)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group the variable dataset will be
        removed from.
      variable (ASCIIString): The variable title to remove from the product
        group.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if the variable dataset is defined in the product group.
    if !has(database[product], variable)
        return false
    end

    # Delete the variable dataset.
    o_delete(database[product], variable)

    # Return successful.
    return true
end

function removeVariableFromList(variable::ASCIIString)
    #=
    Remove a variable from the list of variables held in a database.

    Args:
      base (HDF5File): The HDF5 base file.
      variable (ASCIIString): The variable to remove from the list.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Open the base file.
    base = h5open(BASE_SOURCE, "r+")

    # Get the previous variable list.
    variables = read(base["vars"])

    # Iterate through variables and remove the stated variable.
    for i = 1 : length(variables)
        if variables[i] == variable
            deleteat!(variables, i)
            break
        end
    end

    # Remove the old variable list from the database.
    o_delete(base, "vars")

    # Write the new variable list to the database.
    base["vars"] = variables

    # Close the base file.
    closeDB(base)

    # Return successful.
    return true
end

function setAttribute(database::HDF5File, product::ASCIIString, attribute::ASCIIString, value::Any)
    #=
    Set an attribute of a product group. (High Frequency)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group the attribute will be added to.
      attribute (ASCIIString): The title of the attribute to add.
      value (Any): What the value of the attribute will be.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if the attribute is already defined in the product group, if so
    # remove it
    if exists(attrs(database[product]), attribute)
        a_delete(database[product], attribute)
    end

    # Set the attribute.
    attrs(database[product])[attribute] = value

    # Return successful.
    return true
end

function setVariable(database::HDF5File, product::ASCIIString, variable::ASCIIString, values::Array{Float64,2})
    #=
    Set a variable dataset in a product group. (High Frequency)

    Args:
      database (HDF5File): The HDF5 database file.
      product (ASCIIString): The product group the variable dataset will be
        set to.
      variable (ASCIIString): The variable title to add to the product group.
      values (Array{Float64,1}): The variable dataset to add to the product
        group.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Check if the variable dataset is defined in the product group.
    if has(database[product], variable)
        o_delete(database[product], variable)
    end

    # Create the new variable dataset.
    database[product][variable] = values

    # Return successful.
    return true
end

############################################################### Input Functions

function record(product::ASCIIString, variable::ASCIIString, data::Array{Float64,1}, dates::Array{Date,1}, sku::Int64=-1, overwrite::Bool=true)
    #=
    Record/add new variable data into the database. (High Frequency)

    Args:
      product (ASCIIString): The product name for the dataset.
      variable (ASCIIString): The variable name of the dataset.
      data (Array{Float64,1}): The dataset to be recorded.
      dates (Array{Float64,1}): The date for each data point.
      sku (Int64, optional): Only used when the product is new.
      overwrite (Bool, optional): True to overwrite old data, false otherwise.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Make sure the length of the data and dates arrays are the same.
    datesLength = length(dates)
    if length(data) != datesLength
        error("record: The length of 'data' and 'dates' must be the same.")
    end

    # Open the database.
    database = openDB()

    # Check if the product has been created.
    if !has(database, product)
        addProduct(database, product, Dict(["sku"], sku))
    end

    # Convert dates to integer dates.
    intDates = toIntDate(dates)

    # Check if the variable has been created.
    if has(database[product], variable)
        # The variable has been previously defined so get the old data.
        oldData = getVariable(database, product, variable)

        # Combine the data by the dates.
        newData = hcat(intDates, data)
        mergedData = mergeData(oldData, newData, overwrite)

        # Add the new data into the database.
        setVariable(database, product, variable, mergedData)
    else
        # No variable has been defined, so add the data to the new variable.
        mergedData = hcat(intDates, data)
        setVariable(database, product, variable, mergedData)
    end

    # Close the database.
    closeDB(database)

    # Return successful.
    return true
end

############################################################## Helper Functions

function checkMissingProducts()
    #=
    Check the database for temporary product group names.

    Args:
      None

    Returns:
    Array{Int64,1}: 
    =#

    # Open the database.
    database = openDB()

    # Check all product groups for temporary titles ("TEMP").
    products = names(database)
    temporary(x) = x[1 : 4] == "TEMP"
    tempIndex = find(temporary, products)

    # Close the database.
    closeDB(database)

    # Return the list of temporary product group's skus.
    return products[tempIndex]
end

function checkMissingSkus()
    #=
    Check the database for product groups with missing skus.

    Args:
      None

    Returns:
      Array{ASCIIString,1}: 
    =#

    # Open the database.
    database = openDB()

    # Check all product groups for missing skus (-1).
    products = names(database)
    missing(x) = read(attrs(database[x])["sku"]) == -1
    missIndex = find(missing, products)

    # Close the database.
    closeDB(database)

    # Return the list of product groups with missing skus.
    return products[missIndex]
end

function findNextTemp()
    #=
    Find the next number for naming temporary product groups.

    Args:
      None

    Returns:
      Int64: The next temporary count.
    =#

    # Open the database.
    database = openDB()

    # Pull the product names from the database.
    products = names(database)

    # Set a function to check for a "TEMP" string.
    temporary(x) = x[1 : 4] == "TEMP"

    # Find the indeces of the "TEMP" products.
    tempIndex = find(temporary, products)

    # If no temporary product group exists return 1.
    if length(tempIndex) == 0
        return 1
    end

    # Get a list of the temps and extract the numerical parts.
    temps = products[tempIndex]
    tempNumber = []
    for temp in temps
        tempNumber = vcat(tempNumber, int(temp[6 : end]))
    end

    # Close the database.
    closeDB(database)

    # Return the maximum temporary value plus one.
    return maximum(tempNumber) + 1
end

function fromIntDate(intDate::Int64)
    #=
    Convert an integer date back into Date objects.

    Args:
      intDate (Int64): The integer date to convert back.

    Returns:
      Date: The date object.
    =#

    # Calculate the year, month, and day.
    year = int(floor(intDate / 10000))
    month = int(floor(intDate / 100) - 100 * year)
    day = int(intDate - 10000 * year - 100 * month)

    # Return the year, month, and day.
    return Date(year, month, day)
end

function fromIntDate(intDates::Array{Int64,1})
    #=
    Convert integer dates back into Date objects.

    Args:
      intDates (Array{Int64,1}): The integer dates to convert back.

    Returns:
      Array{Date,1}: The date objects.
    =#

    # Initialize variables.
    lengthDates = length(intDates)
    dates = Array(Date, lengthDates)

    # Iterate through the array, calling the single time function.
    for i = 1 : lengthDates
        dates[i] = fromIntDate(intDates[i])
    end

    # Return the converted dates.
    return dates
end

function mergeData(oldData::Array{Float64,2}, newData::Array{Float64,2}, overwrite::Bool)
    #=
    Merge two datasets where the first column is an integer date.

    Args:
      oldData (Array{Float64,2}): The old data.
      newData (Array{Float64,2}): The new data.
      overwrite (Bool): True to overwrite old data, false otherwise.

    Returns:
      Array{Float64,2}: The merged data.
    =#

    # Concatenate the data together and sort it by the date column.
    merged = vcat(oldData, newData)
    onlyFirst(x) = x[1]
    merged = sortrows(merged, by=onlyFirst)

    # Loop through a the merged data and find repeats.
    (rows, cols) = size(merged)
    repeats = bool(zeros(rows))
    for i = 2 : rows
        if int(merged[i - 1, 1]) == int(merged[i, 1])
            repeats[i] = true
        end
    end

    # If overwriting, switch which repeated value is removed.
    if overwrite
        for j = 2 : rows
            if repeats[j] == true
                repeats[j - 1] = true
                repeats[j] = false
            end
        end
    end

    # Return only the nonrepeating indeces.
    return merged[!repeats, :]
end

function toIntDate(date::Date)
    #=
    Convert a Date object into a single integer representation of the date.

    Args:
      date (Date): The date object.

    Returns:
      Int64: The integer representation of the date.
    =#

    # Return the integer date.
    return year(date) * 10000 + month(date) * 100 + day(date)
end

function toIntDate(dates::Array{Date,1})
    #=
    Convert Date objects into single integer representations of the dates.

    Args:
      dates (Array{Date,1}): The date objects.

    Returns:
      Array{Int64,1}: The integer representations of the dates.
    =#

    # Initialize variables.
    lengthDates = length(dates)
    intDates = Array(Int64, lengthDates)

    # Iterate through the array, calling the single time function.
    for i = 1 : lengthDates
        intDates[i] = toIntDate(dates[i])
    end

    # Return the converted dates.
    return intDates
end

#end # module Database
