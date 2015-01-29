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
include("preprocess.jl")
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
function runLinearModel(product::ASCIIString)
    #=



    =#

    (data, vars) = getProductVariableData(product)
    vars = convert(Array{ASCIIString,1}, vars)

    (dates, data, vars) = combineByDate(data, vars)

    # Find the amount of usable data across selected variables.
    nonNaN = cutTo(data)

    # Cut to the usable observation count.
    dataCut = data[nonNaN + 1 : end, :]
    datesCut = dates[nonNaN + 1 : end, :]

    # Extract the dependent variable.
    depVarIndex = findfirst(vars, "Finished Goods")
    depVar = dataCut[:, depVarIndex]

    # Remove that column.
    indVars = removeColumns(dataCut, [depVarIndex])

    # Add a bias column to the independent vars.
    indVars = hcat(ones(size(indVars, 1)), indVars)

    # Solve for the coefficients.
    coefs = indVars \ depVar

    # Determine the fitted values.
    fitted = indVars * coefs

    # Return the coefficients and fitted values.
    return coefs, fitted
end

function runOverlapModel(product::ASCIIString)
    #=



    =#


    (data, vars) = getProductVariableData(product)
    vars = convert(Array{ASCIIString,1}, vars)

    (dates, data, vars) = combineByDate(data, vars)

    nonNaN = cutTo(data)

    dataCut = data[nonNaN + 1 : end, :]
    datesCut = dates[nonNaN + 1 : end, :]

    depVarIndex = findfirst(vars, "Finished Goods")
    depVar = dataCut[:, depVarIndex]

    indVars = removeColumns(dataCut, [depVarIndex])

    indVars = hcat(ones(size(indVars, 1)), indVars)

    months = month(datesCut)
    depVarSep = Array(Array{Float64,1}, 12)
    indVarsSep = Array(Array{Float64,2}, 12)
    for i = 1 : size(indVars, 1)
        try
            depVarSep[months[i]] = vcat(depVarSep[months[i]], depVar[i])
            indVarsSep[months[i]] = vcat(indVarsSep[months[i]], indVars[i, :])
        catch
            depVarSep[months[i]] = [depVar[i]]
            indVarsSep[months[i]] = indVars[i, :]
        end
    end

    coefs = Array(Array{Float64,1}, 12)
    fitted = Array(Array{Float64,1}, 12)
    for j = 1 : 12
        coefs[j] = indVarsSep[j] \ depVarSep[j]
        fit[j] = indVarsSep[j] * coefs[j]
    end

    return coefs, fit
end
###############################################################################

############################################################## Helper Functions
function combineByDate(dataIn::Array{Array{Float64,2},1}, variablesIn::Array{ASCIIString,1})
    #=


    =#

    data = copy(dataIn)
    variables = copy(variablesIn)

    dataLength = length(data)

    # Find the minimum first index and use it as a base.
    minDate = Inf
    minIndex = 0
    for i = 1 : dataLength
        if data[i][1] < minDate
            minDate = data[i][1]
            minIndex = i
        end
    end

    # Find the shift for padding.
    deltaI = Array(Int64, dataLength)
    for j = 1 : dataLength
        diff = data[j][1] - minDate
        deltaY = floor(diff / 10000)
        deltaM = floor(diff / 100) - deltaY * 100
        if deltaM > 12
            deltaM = 12 - (100 - deltaM)
        end
        deltaI[j] = int(deltaY * 12 + deltaM)
    end

    # Shift the indices padding the beggining with NaN.
    dates = data[minIndex][1 : end - 1, 1]
    dates = fromIntDate(int(dates))
    comb = data[minIndex][1 : end - 1, 2]
    newVars = variables[minIndex]
    for k = 1 : dataLength
        if k != minIndex
            newVars = vcat(newVars, variables[k])
            dataFiller = repmat([NaN], deltaI[k])
            dateFiller = data[minIndex][1 : deltaI[k], 1]
            filler = hcat(dateFiller, dataFiller)
            data[k] = vcat(filler, data[k])
            try
                comb = hcat(comb, data[k][:, 2])
            catch
                comb = hcat(comb, data[k][1 : end - 1, 2])
            end
        end
    end

    # 


    return dates, comb, newVars
end

function cutTo(data)
    #=




    =#


    (obs, vars) = size(data)
    count = zeros(vars)
    for i = 1 : vars
        for j = 1 : obs
            count[i] = count[i] + isnan(data[j, i])
        end
    end

    return int(maximum(count))
end
###############################################################################
