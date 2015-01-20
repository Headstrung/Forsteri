#module Model
#=
Model



Needs:


Examples:


To Do:

=#

############################################################### Use Declaration
include("database.jl")
include("movingaverages.jl")
###############################################################################

############################################################### Model Functions
function linearModel(dep, ind...)
    #=




    =#


end

function ()

end
###############################################################################

############################################################# Analyze Functions

###############################################################################

########################################################## Mass Model Functions
function runModel(product::ASCIIString)
    #=



    =#

    # Open the HDF5 Database file.
    database = h5open(DATABASE_SOURCE, "r")

    # Get the variable titles list.
    variableTitles = names(database[product])

    # Extract all of the variables.
    numOfVars = length(variableTitles)
    variables = Array(Array{Float64,2}, numOfVars)
    for i = 1 : numOfVars
        variables[i] = read(database[product][variableTitles[i]])
    end

    # Close the database file.
    close(database)

    return variables
end
###############################################################################

############################################################## Helper Functions
function combineByDate(data::Array{Array{Float64,2},1})
    #=



    =#

    # Find the number of dates.
    numOfDates = 0
    for i = 1 : length(data)
        numOfDates += size(data[i], 1)
    end

    # Extract the dates.
    count = 0
    dates = Array(Float64, numOfDates)
    for j = 1 : length(data)
        for k = 1 : size(data[j], 1)
            count += 1
            dates[count] = data[j][k, 1]
        end
    end

    datesAct = fromIntDate(int(dates))

    datesAll = [minimum(datesAct) : Month(1) : maximum(datesAct)]
    dataAll = Array(Float64, length(datesAll), length(dates))


    for ii = 1 : length(data)
        for jj = 1 : length()
            if datesAll[jj] == fromIntDate(int(data[ii][jj, 1]))
                dataAll[jj, ii] = data[ii][jj, 2]
            end
        end
    end

    return 
end
###############################################################################
