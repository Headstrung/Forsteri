#module Preprocess
#=
Preprocess

This module contains the algorithms used for preprocessing data from an input
file and preparing it to be written to the database.

Needs:
  Dates

Examples:
  importMultiTime("../data/2014-12.csv", "finished-goods", "mm/yy")

To Do:
  
=#

############################################################### Use Declaration
include("database.jl")
import Base.lowercase
###############################################################################

########################################################## Constant Declaration
const DATE_SEPARATORS = ['/', '-', ':', '.', ' ']
const MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
###############################################################################

############################################################### Write Functions
function writeGeneric(data::Array{Any,2}, header::Array{Any,2}, variable::ASCIIString)
    #=
    Write the generic form of data into the database.

    Args:
      data (Array{Any,2}): The data to be written to the database.
      header (Array{Any,2}): The header values including dates.
      variable (ASCIIString): The variable the dataset represents.

    Returns:
      Bool: True if successful, false otherwise.
    =#

    # Convert the basis values into the proper type.
    if isa(data[1, 1], Number)
        # The basis are numerical, so they must be skus.
        basis = convert(Array{Int64,1}, data[:, 1])
    else
        # The basis are nonumerical, so they must be product codes.
        basis = convertArray(data[:, 1])
    end

    # Check if the basis values are in the database and convert them to
    # product codes if skus.
    (available, missing) = convertBasis(basis)

    # Loop through each column adding the available data to the database.
    for (product, index) in available
        (dataFinal, headerFinal) = trimLeadingZeros(convert(Array{Float64,1}, vec(data[index, 2 : end])), convert(Array{Date,1}, header[2 : end]))
        record(product, variable, dataFinal, headerFinal)
    end
    # Add the missing data to the database, creating temporary titles for
    # missing product codes and flagging missing skus.
    missingType = typeof(missing)
    if missingType == Dict{ASCIIString,Int64}
        # Create new products through the record function and add the data.
        for (product, index) in missing
            record(product, variable, convert(Array{Float64,1}, vec(data[index, 2 : end])), convert(Array{Date,1}, header[2 : end]))
        end
    elseif missingType == Dict{Int64,Int64}
        # Determine the next temporary count.
        tempIndex = findNextTemp()
        # Create new products with the sku given and a temporary title.
        for (sku, index) in missing
            record(string("TEMP-", tempIndex), variable, convert(Array{Float64,1}, vec(data[index, 2 : end])), convert(Array{Date,1}, header[2 : end]), sku)
            tempIndex += 1
        end
    end

    # Return successful.
    return true
end
###############################################################################

########################################################## Preprocess Functions
function importMultiTime(source::ASCIIString, variable::ASCIIString, dateFormat::ASCIIString)
    #=
    Import a timeseries (multi time) file. The file must be in the header
    format [Basis, Date_1, Date_2, ..., Date_n].

    Args:
      source (ASCIIString): The file location on the disk.
      variable (ASCIIString): The variable the file represents.
      dateFormat (ASCIIString): An abstract representation of the date.

    Returns:
      Bool: True if successfully imported, false otherwise.
    =#

    # Make sure the variable is allowed.
    variableList = getVariableList()
    if !(variable in variableList)
        error("importMultiTime: The input variable, ", variable, ", is not a defined variable. Please define it.")
    end

    # Copy the source file to the imported directory and change the name.
    #cp(source, string("../data/imported/", now(), "|", variable))

    # Read the data and header from the file.
    (data, header) = readdlm(source, ',', header=true)

    # Convert the header dates into Date objects.
    headerAny = Array(Any, size(header))
    headerAny[1] = header[1]
    for i = 2 : length(header)
        headerAny[i] = str2date(header[i], dateFormat)
    end

    # Zero out missing data.
    data = zeroOut(data)

    # Sort the data.
    (data, headerAny) = sortAll(data, headerAny)

    # Aggregate repeats.
    (data, repeats) = aggregate(data)

    # Rediscretize to monthly.
    (data, headerAny) = rediscretize(data, headerAny, 'm')

    # Write the data to the database.
    writeGeneric(data, headerAny, variable)

    # Return successful.
    return true
end

function importMultiMultiTime(source::ASCIIString, dateFormat::ASCIIString, walmart::Bool)
    #=
    Import a timeseries (multi time) file with multiple variables. The file
      must be in the header format [Basis, Var._1, Var._2, ..., Var._n, Date].

    Args:
      source (ASCIIString): The file location on the disk.
      dateFormat (ASCIIString): Abstract representation of the date.

    Returns:
      Bool: True if successfully imported, false otherwise.
    =#

    # Read the data and the header from the file.
    (data, header) = readdlm(source, ',', header=true)

    # Reduce the file and set the headers to be the correct variable names.
    (dataNew, headerNew) = reduceData(data, header)

    # Find the column index that represents the date.
    dateColumn = findfirst(headerNew, "date")

    # If no date column is found, throw an error.
    if dateColumn == 0
        error("importMultiMultiTime: No date column was found.")
    end

    # Extract the date column.
    datesStr = dataNew[:, dateColumn]

    # Create the new dates array.
    dates = Array(Date, length(datesStr))

    # If the imported dates are numbers, convert to a string.
    if isa(datesStr[1], Number)
        datesStr = convertArray(int(datesStr))
    end

    # Convert the date column into Date objects.
    for i = 1 : length(datesStr)
        dates[i] = str2date(datesStr[i], dateFormat, walmart)
    end

    # Find basis column.
    basisColumn = findfirst(headerNew, "basis")

    # If no basis column is found, throw an error.
    if basisColumn == 0
        error("importMultiMultiTime: No basis column was found.")
    end

    # Extract the basis column.
    basis = dataNew[:, basisColumn]

    # Remove the date and basis columns from the data.
    (dataNew, headerNew) = removeColumns(dataNew, [basisColumn, dateColumn], headerNew)

    # Find the starting index of each repeated basis.
    (obs, vars) = size(dataNew)
    check = basis[1]
    starts = [1]
    for j = 2 : obs
        if basis[j] != check
            check = basis[j]
            starts = vcat(starts, j)
        end
    end

    # Break the data into separate arrays for each basis.
    startsLength = length(starts)
    separate = Array(Any, startsLength)
    for k = 1 : startsLength - 1
        separate[k] = dataNew[starts[k] : starts[k + 1] - 1, :]
    end
    separate[end] = dataNew[starts[end] : end, :]

    pvData = []
    for ii = 1 : startsLength
        for jj = 1 : length(headerNew)
            pvData = separate[ii][:, jj]

            if ii != startsLength
                currentDates = dates[starts[ii] : starts[ii + 1] - 1]
            else
                currentDates = dates[starts[ii] : end]
            end
            (dada, cont) = rediscretize(vcat(basis[starts[ii]], separate[ii][:, jj])', vcat("basis", currentDates)', 'm')
            writeGeneric(dada, cont, headerNew[jj])
        end
    end

    return true
end

function importMultiSingleTime(sources::Array{ASCIIString,1}, dates::Array{Date,1}, singular::Bool=true)
    #=
    Import multiple single time files and stitch them together as if they were
    a timeseries. The files must all have the same header format
    [Basis, Var._1, Var._2, ..., Var._n] and the index of the source must match
    the index of the date.

    Args:
      sources (Array{ASCIISting,1}): The file locations on the disk.
      dates (Array{Date,1}): The dates the files represent.
      singular (Bool): True if the inputs are singular, false otherwise.

    Returns:
      Bool: True if successfully imported, false otherwise.
    =#

    # Check to make sure there is a date for each source.
    if length(sources) != length(dates)
        error("importMultiSingleTime: the lengths of 'sources' and 'dates' must match.")
    end

    # Initialize variables.
    sourcesLength = length(sources)
    datesLength = length(dates)
    allData = Array(Any, sourcesLength, 1)
    header = []

    # Import each file.
    for i = 1 : sourcesLength
        (allData[i], header) = importSingleTime(sources[i], dates[i])
    end

    # Initialize variables for separating the data.
    variables = header[2 : end]
    variablesLength = length(variables)
    full = Array(Any, datesLength, 1)
    combData = Array(Any, variablesLength, 1)

    # Separate the variables and create a multi time.
    for j = 1 : variablesLength
        for k = 1 : datesLength
            full[k] = hcat(allData[k][:, 1], allData[k][:, j + 1])
        end
        combData[j] = stitch(full)
    end

    # Set the headers with dates.
    timeHeader = vcat(header[1], dates)

    # Match the dates with the proper discretization.
    if singular
        # Change the dates to match the database convention.
        # Could call singularCut() here.
        for ii = 2 : datesLength + 1
            timeHeader[ii] = Date(year(timeHeader[ii]), month(timeHeader[ii]), 1)
        end
    else
        # Rediscretize for nonsingular variables.
        # If a list of nonsingular variables is input do for var in nonSing.
        for jj = 1 : variablesLength
            (combData[jj], timeHeader) = rediscretize(combData[jj], timeHeader, 'm')
        end
    end

    # Write the data to the database.
    for kk = 1 : variablesLength
        writeGeneric(combData[kk], timeHeader', convert(ASCIIString, variables[kk]))
    end

    # Return successful.
    return true
end

function importSingleTime(source::ASCIIString, date::Date)
    #=
    Import a single time file. The file must be in the header format
    [Basis, Var._1, Var._2, ..., Var._n].

    Args:
      source (ASCIIString): The file location on the disk.
      date (ASCIIString): The date the file represents.

    Returns:
      Array{Any,2}: The data extracted from the file.
      Array{Any,2}: The header extracted from the file.
    =#

    # Read the data and header from the file.
    (data, header) = readdlm(source, ',', header=true)

    # Sort the data.
    (data, header) = sortAll(data, header)

    # Aggregate repeats.
    (data, repeats) = aggregate(data)

    # Return the data and header.
    return data, header
end
###############################################################################

############################################################## Helper Functions
function aggregate(data::Array{Any,2})
    #=
    Aggregate (sum) the data over repeated first column values. The data must
    be row sorted already.

    Args:
      data (Array{Any,2}): The data to be aggregated.

    Returns:
      Array{Any,2}: The data after being aggregated.
    =#

    # Initialize variables.
    (rows, cols) = size(data)
    temp = data[1, 2 : end]
    agg = Array(Any, rows, cols)

    # Loop through the rows and aggregate repeats.
    for i = 2 : rows
        if data[i, 1] == data[i - 1, 1]
            temp += data[i, 2 : end]
        else
            agg[i - 1, :] = hcat(data[i - 1, 1], temp)
            temp = data[i, 2 : end]
        end
    end
    agg[end, :] = hcat(data[end, 1], temp)

    # Check which rows are defined.
    rowsDefined = []
    for j = 1 : rows
        if isdefined(agg, j, 1)
            rowsDefined = vcat(rowsDefined, j)
        end
    end

    # Determine number of repeats.
    repeats = vcat(rowsDefined[1], rowsDefined[2 : end] - rowsDefined[1 : end - 1])

    # Return only the defined rows and number of repeats.
    return agg[rowsDefined, :], repeats
end

function convertArray(array::Array{Int64,1})
    #=



    =#

    # Initialize variables.
    arrayLength = length(array)
    newArray = Array(ASCIIString, arrayLength)

    # Convert each element of the array into a string.
    for i = 1 : arrayLength
        newArray[i] = string(array[i])
    end

    # Return the converted array.
    return newArray
end

function convertArray(array::Array{Any,1})
    #=
    Convert an array of type Any to an array of type ASCIIString.

    Args:
      array (Array{Any,1}): The array to be converted.

    Returns:
      Array{ASCIIString,1}: The converted to a string array.
    =#

    # Initialize variables.
    arrayLength = length(array)
    newArray = Array(ASCIIString, arrayLength)

    # Convert each element of the array into a string.
    for i = 1 : arrayLength
        newArray[i] = string(array[i])
    end

    # Return the converted array.
    return newArray
end

function convertBasis(basis::Array{ASCIIString,1})
    #=
    Check if the product codes in a basis array are in the database.

    Args:
      basis (Array{ASCIIString,1}): An array of the product codes to be
        checked.

    Returns:
      Dict{ASCIIString,Int64}: The currently defined basis of product codes
        linked to their original index.
      Dict{ASCIIString,Int64}: The missing product codes from the database
        linked to their original index.
    =#

    # Initialize variables.
    available = (ASCIIString => Int64)[]
    missing = (ASCIIString => Int64)[]

    # Get the sku to code hash table.
    basisList = getProductList()
    basisLength = length(basis)

    # Loop through the basis array and check if it is in the database.
    for i = 1 : basisLength
        if basis[i] in basisList
            available[basis[i]] = i
        else
            missing[basis[i]] = i
        end
    end

    # Return dictionaries pointing each available and missing product to its
    # original index.
    return available, missing
end

function convertBasis(basis::Array{Int64,1})
    #=
    Check if the sku codes in a basis array are in the database.

    Args:
      basis (Array{Int64,1}): An array of the sku codes to be checked.

    Returns:
      Dict{ASCIIString,Int64}: The currently defined basis of product codes
        linked to their original index.
      Dict{Int64,Int64}: The missing product codes from the database
        linked to their original index.
    =#

    # Initialize variables.
    available = (ASCIIString => Int64)[]
    missing = (Int64 => Int64)[]

    # Get the sku to code hash table.
    basisHash = getBasisHash()
    basisLength = length(basis)

    # Get the sku codes.
    basisCodes = keys(basisHash)

    # Loop through the basis array and check if it is in the database.
    for i = 1 : basisLength
        if basis[i] in basisCodes
            available[basisHash[basis[i]]] = i
        else
            missing[basis[i]] = i
        end
    end

    # Return dictionaries pointing each available and missing product to its
    # original index.
    return available, missing
end

function lowercase(x::Array{ASCIIString,1})
    #=
    Convert an array of strings to all lowercase.

    Args:
      x (Array{ASCIIString,1}): The array of strings to convert to lowercase.

    Returns:
      Array{ASCIIString,1}: The lowercase array of strings.
    =#

    # Initialize variables.
    xLength = length(x)
    xLower = Array(ASCIIString, xLength)

    # Convert each element to lowercase.
    for i = 1 : xLength
        xLower[i] = lowercase(x[i])
    end

    # Return the new array.
    return xLower
end

function reduceData(data::Array{Any,2}, header::Array{String,2}, remove::Array{Int64,1}=[-1])
    #=
    Remove unecessary columns from a file, match the headers with known
    variables, and write the file into the 'imported' directory.

    Args:
      data (Array{Any,2}): The data.
      header (Array{String,2}): The header.
      remove (Array{Int64,1}): An array of index locations representing
        columns that should be removed.

    Returns:
      Array{Any,2}: 
      Array{String,2}
    =#

    # Remove the designated columns.
    if remove[1] != -1
        (data, header) = removeColumns(data, remove, header)
    end

    # Make a copy for comparison.
    dataNew = copy(data)
    headerNew = copy(header)
    headerLower = lowercase(convert(Array{ASCIIString,1}, vec(headerNew)))

    # Get the dictionary relating variables to titles.
    variableDict = getVariableToTitle()

    # Create an empty vector to record missing titles in the base file.
    missing = []
    ignore = []

    # Loop through the headers and find the name of each.
    for i = 1 : length(headerNew)
        for (variable, titles) in variableDict
            if headerLower[i] in titles
                headerNew[i] = variable
                if variable == "ignore"
                    ignore = vcat(ignore, i)
                end
                break
            end
        end

        # Catch the missing condition.
        if headerNew[i] == header[i]
            missing = vcat(missing, i)
        end
    end

    # Add all missing titles to the missing variable.
    if length(missing) > 0
        addToVariableTitles("missing", headerLower[missing])
    end

    # Remove ignored and missing columns.
    (dataNew, headerNew) = removeColumns(dataNew, vcat(missing, ignore), headerNew)

    # Return the new data and header.
    return dataNew, headerNew'
end

function rediscretize(data::Array{Any,2}, header::Array{Any,2}, to::Char)
    #=
    Rediscretize by aggregation to a higher level discretization. The dates in
    the header must already be converted to Date objects.

    Args:
      data (Array{Any,2}): The data to be rediscretized.
      header (Array{Any,2}): The header.
      to (Char): A character representing the desired discretization. Can be
        'w', 'm', 'q', or 'y'.

    Returns:
      Array{Any,2}: The new rediscretized data.
      Array{Any,2}: The new header.
    =#

    # Make a copy of the data transposed.
    dataCopy = vcat(header, data)'
    (rows, cols) = size(dataCopy)

    if to == 'm'
        # Set all dates within a single month to be the same date.
        for i = 2 : rows
            dataCopy[i, 1] = Date(year(dataCopy[i, 1]), month(dataCopy[i, 1]), 1)
        end
    elseif to == 'y'
        for j = 2 : rows
            dataCopy[i, 1] = Date(year(dataCopy[i, 1]), 1, 1)
        end
    else
        error("rediscretize: Functionality for to: '", to, "' not yet implemented.")
    end

    # Aggregate over the common dates.
    (dataCopy, repeats) = aggregate(dataCopy)

    # Return the rediscretized data and header.
    return dataCopy[:, 2 : end]', dataCopy[:, 1]'
end

function removeColumns(data::Array{Any,2}, remove::Array{Int64,1}, header::Array{String,2}=[""])
    #=
    Remove a list of columns from data.

    Args:
      data (Array{Any,2}): The data.
      remove (Array{Int64,1}): An array of index locations representing
        columns that should be removed.
      header (Array{String,2}, optional): The header.

    Returns:
      Array{Any,2}: The data with the given columns removed.
      Array{String,2}, optional: The header with the given columns removed.
    =#

    # Create a vector of the column indices to keep.
    keep = [1 : size(data)[2]]

    # Remove any indices given by the remove array.
    deleteat!(keep, remove)

    # Return the data with the columns removed and the header if given.
    if length(header[1]) == 0
        return data [:, keep]
    else
        return data[:, keep], header[keep]
    end
end

function removeColumns(data::Array{Any,2}, remove::Array{Int64,1}, header::Array{ASCIIString,1}=[""])
    #=
    Remove a list of columns from data.

    Args:
      data (Array{Any,2}): The data.
      remove (Array{Int64,1}): An array of index locations representing
        columns that should be removed.
      header (Array{String,2}, optional): The header.

    Returns:
      Array{Any,2}: The data with the given columns removed.
      Array{String,2}, optional: The header with the given columns removed.
    =#

    # Create a vector of the column indices to keep.
    keep = [1 : size(data)[2]]

    # Remove any indices given by the remove array.
    deleteat!(keep, remove)

    # Return the data with the columns removed and the header if given.
    if length(header[1]) == 0
        return data [:, keep]
    else
        return data[:, keep], header[keep]
    end
end

function singularCut(data::Array{Array,2}, header::Array{Any,2}, to::Char)
    #=
    *** This function may be necissary if I want the user to be able to input
    a singular variable on a higher discretization than what they desire. For
    now the user must input the discretization they desire at the time of
    upload.
    For variables that are singular cut to the specified discretization.



    =#
end

function stitch(data::Array{Any,2})
    #=
    Combine an array of arrays matching the first columns where each major
    index is appended.

    Args:
      data (Array{Any,2}): The multidimentional array to be combined.

    Returns:
      Array{Any,2}: The new stitched together array.
    =#

    # Copy data and initialize variables.
    dataCopy = copy(data)
    (ds, arb) = size(dataCopy)

    # Find the maximum number of rows in all of the data and its index.
    maxRows = -1
    maxIndx = 0
    for i = 1 : ds
        rows = size(dataCopy[i])[1]
        if rows > maxRows
            maxRows = rows
            maxIndx = i
        end
    end

    # Initialize the final stitched array.
    final = Array(Any, maxRows, ds + 1)
    final[:, 1] = dataCopy[maxIndx][:, 1]

    # Match each first column with the output's first column.
    for j = 1 : ds
        rows = size(dataCopy[j])[1]
        for k = 1 : rows
            for ii = 1 : maxRows
                if dataCopy[j][k, 1] == final[ii, 1]
                    final[ii, j + 1] = dataCopy[j][k, 2]
                    break
                end
            end
        end
    end

    # Zero out any undefined data.
    final = zeroOut(final)

    # Return the stitched data.
    return final
end

function sortAll(data::Array{Any,2}, header::Array{Any,2})
    #=
    Sort the rows based on the first column and the columns based on the
    header.

    Args:
      data (Array{Any,2}): The data to be sorted.
      header (Array{Any,2}): The header to be sorted.

    Returns:
      Array{Any,2}: The sorted data.
      Array{Any,2}: The sorted header.
    =#

    # Make copies of the data and header as to not alter the original.
    dataCopy = copy(data)
    headerCopy = copy(header)

    # Sort the data such that the rows are ordered by the IDs and the
    # columns are ordered by the header dates.
    dataCopy = vcat(headerCopy, sortrows(dataCopy))
    dataCopy = hcat(dataCopy[:, 1], sortcols(dataCopy[:, 2 : end]))

    # Return the new sorted data and header.
    return dataCopy[2 : end, :], dataCopy[1, :]
end

function sortAll(data::Array{Float64,2}, header::Array{String,2})
    #=
    Sort the rows based on the first column and the columns based on the
    header.

    Args:
      data (Array{Float64,2}): The data to be sorted.
      header (Array{String,2}): The header to be sorted.

    Returns:
      Array{Any,2}: The sorted data.
      Array{Any,2}: The sorted header.
    =#

    # Make copies of the data and header as to not alter the original.
    dataCopy = copy(data)
    headerCopy = copy(header)

    # Sort the data such that the rows are ordered by the IDs and the
    # columns are ordered by the header dates.
    dataCopy = vcat(headerCopy, sortrows(dataCopy))
    dataCopy = hcat(dataCopy[:, 1], sortcols(dataCopy[:, 2 : end]))

    # Return the new sorted data and header.
    return dataCopy[2 : end, :], dataCopy[1, :]
end

function sortAll(data::Array{Any,2}, header::Array{String,2})
    #=
    Sort the rows based on the first column and the columns based on the
    header.

    Args:
      data (Array{Float64,2}): The data to be sorted.
      header (Array{String,2}): The header to be sorted.

    Returns:
      Array{Any,2}: The sorted data.
      Array{Any,2}: The sorted header.
    =#

    # Make copies of the data and header as to not alter the original.
    dataCopy = copy(data)
    headerCopy = copy(header)

    # Sort the data such that the rows are ordered by the IDs and the
    # columns are ordered by the header dates.
    dataCopy = vcat(headerCopy, sortrows(dataCopy))
    dataCopy = hcat(dataCopy[:, 1], sortcols(dataCopy[:, 2 : end]))

    # Return the new sorted data and header.
    return dataCopy[2 : end, :], dataCopy[1, :]
end

function trimLeadingZeros(data::Array{Float64,1}, header::Array{Date,1})
    #=
    Remove leading zeros from the dataset. This assumes the data is already
    ordered chronologically.

    Args:
      data (Array{Float64,1}): 

    Returns:
      Array{Float64,1}: The data with leading zeros removed.
    =#

    # Find the first nonzero element.
    for i = 1 : length(data)
        if data[i] != 0.0
            first = i

            # Return the data from the first nonzero element to the end.
            return data[i : end], header[i : end]
        end
    end

    # If no nonzero elements exist, return the last element.
    return [data[end]], [header[end]]
end

function zeroOut(data::Array{Any,2})
    #=
    Add zeros to a dataset where ever missining data exists.

    Args:
      data (Array{Any,2}): The data to zero out.

    Returns:
      Array{Any,2}: The data with zeros substituted for empty strings.
    =#

    # Initialize variables.
    (rows, cols) = size(data)

    # Loop through all elements of the array setting "" to 0.
    for j = 1 : cols, i = 1 : rows
        if !isdefined(data, i, j) || data[i, j] == ""
            data[i, j] = 0.0
        end
    end

    # Return the new data.
    return data
end
###############################################################################

################################################### Date Manipulation Functions
function ord2date(dayOfYear::Int64, year::Int64)
    #=
    Convert an ordinal date to a Date object.

    Args:
    dayOfYear (Int64): The day number within a year.
    year (Int64): The year.

    Returns:
      Date: The converted ordinal date to a Date object.
    =#

    # Initialize the start days for each month.
    monthStarts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

    # If it is a leap year add a day to the correct months.
    if year % 4 == 0
        monthStarts = vcat(monthStarts[1 : 2], monthStarts[3 : end] + 1)
    end

    # Determine the month of the day of year.
    if dayOfYear < monthStarts[2]
        month = 1
    elseif dayOfYear < monthStarts[3]
        month = 2
    elseif dayOfYear < monthStarts[4]
        month = 3
    elseif dayOfYear < monthStarts[5]
        month = 4
    elseif dayOfYear < monthStarts[6]
        month = 5
    elseif dayOfYear < monthStarts[7]
        month = 6
    elseif dayOfYear < monthStarts[8]
        month = 7
    elseif dayOfYear < monthStarts[9]
        month = 8
    elseif dayOfYear < monthStarts[10]
        month = 9
    elseif dayOfYear < monthStarts[11]
        month = 10
    elseif dayOfYear < monthStarts[12]
        month = 11
    else
        month = 12
    end

    # Determine the day of month.
    day = dayOfYear - monthStarts[month] + 1

    # Return the Date object.
    return Date(year, month, day)
end

function str2date(date::ASCIIString, format::ASCIIString, walmart::Bool=false)
    #=
    Convert a string to a date.

    Args:
      date (SubString{ASCIIString}): The date to be converted.
      format (ASCIIString): An abstract representation of the date.

    Returns:
      Date: The converted date into a Date object.
    =#

    # Make sure the lengths of date and format are the same.
    if length(date) != length(format)
        error("str2date: The lengths of 'date' and 'format' must match.")
    end

    # Initialize variables.
    formatLower = lowercase(format)
    year = ""
    month = ""
    week = ""
    day = ""

    # Loop through the format and assign the components of the date.
    for i = 1 : length(formatLower)
        if formatLower[i] in DATE_SEPARATORS
            continue
        elseif formatLower[i] == 'y'
            year = string(year, date[i])
        elseif formatLower[i] == 'm'
            month = string(month, date[i])
        elseif formatLower[i] == 'w'
            week = string(week, date[i])
        elseif formatLower[i] == 'd'
            day = string(day, date[i])
        else
            error("str2date: Functionality for ", format[i], " has not yet been implemented.")
        end
    end

    # Standardize the year.
    yearLength = length(year)

    if yearLength == 4
        # Catch full years and do nothing.
    elseif yearLength == 2
        # Determine the correct millenium when two characters define year.
        currentYear = string(Dates.year(today()))
        if year <= currentYear[3 : 4]
            year = string(currentYear[1 : 2], year)
        else
            year = string(int(currentYear[1 : 2]) - 1, year)
        end
    else
        # Catch nondefined lengths for year and throw an error.
        error("str2date: '", year, "' is not a valid year.")
    end

    # Standardize the day.
    dayLength = length(day)

    if dayLength == 0
        # if no day is given assume first day of month.
        day = "1"
    elseif dayLength < 3
        # Catch possible day lengths and do nothing.
    else
        error("str2date: '", day, "' is not a valid day.")
    end

    # Standardize the month.
    monthLength = length(month)
    monthLower = lowercase(month)

    if monthLength == 0
        # A week number must have been given.
        return week2date(int(year), int(week), int(day), walmart)
    elseif monthLength < 3
        # If less than three characters define month then assume its numerical.
    elseif monthLength == 3
        # Include the first three letters of a month as a valid input.
        for j = 1 : length(MONTHS)
            if monthLower == MONTHS[j][1 : 3]
                month = j
                break
            end
        end
        if typeof(month) == ASCIIString
            error("str2date: '", month, "' is not a valid month.")
        end
    elseif monthLower in MONTHS
        # Determine the full literal month, if given.
        month = findfirst(MONTHS, monthLower)
    else
        # If no previous condition was caught, throw an error.
        error("str2date: '", month, "' is not a valid month.")
    end

    return Date(int(year), int(month), int(day))
end

function str2date(date::SubString{ASCIIString}, format::ASCIIString, walmart::Bool=false)
    #=
    Convert a string to a date.

    Args:
      date (SubString{ASCIIString}): The date to be converted.
      format (ASCIIString): An abstract representation of the date.

    Returns:
      Date: The converted date into a Date object.
    =#

    # Make sure the lengths of date and format are the same.
    if length(date) != length(format)
        error("str2date: The lengths of 'date' and 'format' must match.")
    end

    # Initialize variables.
    formatLower = lowercase(format)
    year = ""
    month = ""
    week = ""
    day = ""

    # Loop through the format and assign the components of the date.
    for i = 1 : length(formatLower)
        if formatLower[i] in DATE_SEPARATORS
            continue
        elseif formatLower[i] == 'y'
            year = string(year, date[i])
        elseif formatLower[i] == 'm'
            month = string(month, date[i])
        elseif formatLower[i] == 'w'
            week = string(week, date[i])
        elseif formatLower[i] == 'd'
            day = string(day, date[i])
        else
            error("str2date: Functionality for ", format[i], " has not yet been implemented.")
        end
    end

    # Standardize the year.
    yearLength = length(year)

    if yearLength == 4
        # Catch full years and do nothing.
    elseif yearLength == 2
        # Determine the correct millenium when two characters define year.
        currentYear = string(Dates.year(today()))
        if year <= currentYear[3 : 4]
            year = string(currentYear[1 : 2], year)
        else
            year = string(int(currentYear[1 : 2]) - 1, year)
        end
    else
        # Catch nondefined lengths for year and throw an error.
        error("str2date: '", year, "' is not a valid year.")
    end

    # Standardize the day.
    dayLength = length(day)

    if dayLength == 0
        # if no day is given assume first day of month.
        day = "1"
    elseif dayLength < 3
        # Catch possible day lengths and do nothing.
    else
        error("str2date: '", day, "' is not a valid day.")
    end

    # Standardize the month.
    monthLength = length(month)
    monthLower = lowercase(month)

    if monthLength == 0
        # A week number must have been given.
        return week2date(int(year), int(week), int(day), walmart)
    elseif monthLength < 3
        # If less than three characters define month then assume its numerical.
    elseif monthLength == 3
        # Include the first three letters of a month as a valid input.
        for j = 1 : length(MONTHS)
            if monthLower == MONTHS[j][1 : 3]
                month = j
                break
            end
        end
        if typeof(month) == ASCIIString
            error("str2date: '", month, "' is not a valid month.")
        end
    elseif monthLower in MONTHS
        # Determine the full literal month, if given.
        month = findfirst(MONTHS, monthLower)
    else
        # If no previous condition was caught, throw an error.
        error("str2date: '", month, "' is not a valid month.")
    end

    return Date(int(year), int(month), int(day))
end

function week2date(year::Int64, week::Int64, day::Int64, walmart::Bool=false)
    #=
    Convert a date in week number format to a Date object. This is an
    implementation of the formula in http://en.wikipedia.org/wiki/
    ISO_week_date#Calculating_a_date_given_the_year.2C_week_number_and_weekday

    Args:
      year (Int64): Year of the date.
      week (Int64): Week of the year.
      day (Int64): Day of the week.
      walmart (Bool, optional): True if the week is a Walmart week, false
        otherwise.

    Returns:
      Date: The converted week version of the date to Date object.
    =#

    # Initlialize the number of days in the year and the ordinal date.
    daysInYear = dayofyear(Date(year, 12, 31))
    ord = week * 7 + day - (dayofweek(Date(year, 1, 4)) + 3)

    # If the ordinal is out of bounds +/- the number of days in the year.
    if ord < 1
        year = year - 1
        ord = ord + dayofyear(Date(year, 12, 31))
    elseif ord > daysInYear
        year = year + 1
        ord = ord - daysInYear
    end

    dateFinal = ord2date(ord, year)
    if walmart
        dateFinal = dateFinal + Month(1)
    end

    # Return the converted ordinal to a Date object.
    return dateFinal
end
###############################################################################

#end # module Preprocess
