module Preprocess
#=
Preprocess

This module contains the algorithms used for preprocessing data from an input
file and preparing it to be written to the database.

Needs:
  Dates

Examples:
  

To Do:
  
=#

using Dates

const MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
const DATE_SEPARATORS = ['/', '-', ':', '.', ' ']

function importMultiTime(source::ASCIIString, variable::ASCIIString, dateFormat::ASCIIString)
    #=
    Import a timeseries (multi time) file. The file must be in the header
    format [Basis, Time_1, Time_2, ..., Time_n].

    Args:
      source (ASCIIString): The file location on the disk.
      variable (ASCIIString): The variable the file represents.
      dateFormat (ASCIIString): An abstract representation of the date.

    Returns:
      Bool: True if successfully imported, false otherwise.
    =#

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

    # Rediscretize if monthly. (Add additional rediscretizations)
    if 'w' in lowercase(dateFormat)
        (data, headerAny) = rediscretize(data, headerAny, 'm')
    end

    # Return the data and header.
    return data, headerAny
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

    # Rediscretize for nonsingular variables.
    if !singular
        for k = 1 : variablesLength
            (combData[k], timeHeader) = rediscretize(combData[k], timeHeader, 'm')
        end
    end

    # Return the data, header, and variables defining each index of combData.
    return combData, timeHeader, variables
end

function importSingleTime(source::ASCIIString, date::Date)
    #=
    Import a single time file. The file must be in the header format
    [Basis, Var._1, Var._2, ..., Var._n].

    Args:
      source (ASCIIString): The file location on the disk.
      date (ASCIIString): The date the file represents.

    Returns:
      Bool: True if successfully imported, false otherwise.
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

function singularCut(data::Array{Array,2}, header::Array{Any,2}, to::Char)
    #=
    *** This function may be necissary if I want the user to be able to input
    a singular variable on a higher discretization than what they desire. For
    now the user must input the discretization they desire at the time of
    upload.
    For variables that are singular cut to the specified discretization.



    =#
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

function str2date(date::SubString{ASCIIString}, format::ASCIIString)
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
        return week2date(int(year), int(week), int(day))
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

function week2date(year::Int64, week::Int64, day::Int64)
    #=
    Convert a date in week number format to a Date object. This is an
    implementation of the formula in http://en.wikipedia.org/wiki/
    ISO_week_date#Calculating_a_date_given_the_year.2C_week_number_and_weekday

    Args:
      year (Int64): Year of the date.
      week (Int64): Week of the year.
      day (Int64): Day of the week.

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

    # Return the converted ordinal to a Date object.
    return ord2date(ord, year)
end

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

end # module Preprocess
